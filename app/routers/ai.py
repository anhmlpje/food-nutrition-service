import os
import json
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.database import get_db
from app import models
from app.auth import get_current_user
from app.utils.nutrition_calc import compute_recipe_nutrition
from sqlalchemy import text

router = APIRouter(prefix="/ai", tags=["AI-Powered Analytics"])

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


class RecommendRequest(BaseModel):
    ingredient_ids: List[int]
    dietary_goal: str = "balanced"  # balanced / high-protein / low-calorie / low-carb


class AnalyseRequest(BaseModel):
    recipe_id: int


async def call_claude(prompt: str) -> str:
    """Send a prompt to Claude and return the text response."""
    if not ANTHROPIC_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="AI service unavailable: ANTHROPIC_API_KEY not configured"
        )

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            ANTHROPIC_API_URL,
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-opus-4-6",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            }
        )

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="AI service returned an error")

    return response.json()["content"][0]["text"]


@router.post("/recommend")
async def recommend_recipes(
    request: RecommendRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Given a list of ingredient IDs and a dietary goal,
    use Claude AI to suggest recipe ideas with preparation tips.
    """
    ingredients = (
        db.query(models.Ingredient)
        .filter(models.Ingredient.id.in_(request.ingredient_ids))
        .all()
    )

    if not ingredients:
        raise HTTPException(status_code=404, detail="No valid ingredients found")

    ingredient_summary = "\n".join([
        f"- {ing.name}: {ing.calories} kcal, {ing.protein}g protein, "
        f"{ing.carbohydrate}g carbs, {ing.fat}g fat per 100g"
        for ing in ingredients
    ])

    prompt = f"""You are a professional nutritionist and chef. 
A user has the following ingredients available:

{ingredient_summary}

Their dietary goal is: {request.dietary_goal}

Please suggest 3 creative recipe ideas using some or all of these ingredients.
For each recipe provide:
1. Recipe name
2. Which ingredients to use and approximate quantities (in grams)
3. Brief preparation method (2-3 sentences)
4. Why this recipe suits their dietary goal

Respond in JSON format with a list of 3 recipe objects."""

    ai_response = await call_claude(prompt)

    return {
        "dietary_goal": request.dietary_goal,
        "ingredients_provided": [ing.name for ing in ingredients],
        "ai_recommendations": ai_response,
    }


@router.post("/analyse")
async def analyse_recipe(
    request: AnalyseRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Use Claude AI to provide a deep health analysis of a recipe,
    including personalised improvement suggestions.
    """
    recipe = db.query(models.Recipe).filter(models.Recipe.id == request.recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if not recipe.ingredients:
        raise HTTPException(status_code=400, detail="Recipe has no ingredients")

    rows = db.execute(
        text("SELECT ingredient_id, quantity_g FROM recipe_ingredients WHERE recipe_id = :rid"),
        {"rid": request.recipe_id}
    ).fetchall()
    qty_map = {row[0]: row[1] for row in rows}

    ingredients_with_qty = [
        {"ingredient": ing, "quantity_g": qty_map.get(ing.id, 100.0)}
        for ing in recipe.ingredients
    ]

    nutrition = compute_recipe_nutrition(ingredients_with_qty)

    nutrition_summary = json.dumps(nutrition["totals"], indent=2)

    prompt = f"""You are an expert nutritionist. Analyse the following recipe and provide health insights.

Recipe: {recipe.name}
Cuisine: {recipe.cuisine_type or "Unknown"}
Difficulty: {recipe.difficulty}

Nutritional content (total for recipe):
{nutrition_summary}

Health Score: {nutrition["health_score"]}/100
Existing warnings: {", ".join(nutrition["warnings"]) if nutrition["warnings"] else "None"}
Allergens detected: {", ".join(nutrition["allergens"]) if nutrition["allergens"] else "None"}

Please provide:
1. Overall health assessment (2-3 sentences)
2. Key nutritional strengths of this recipe
3. Nutritional concerns or weaknesses
4. 3 specific suggestions to improve the nutritional profile
5. Who this recipe is best suited for (e.g. athletes, weight loss, etc.)

Be specific, evidence-based, and practical."""

    ai_response = await call_claude(prompt)

    return {
        "recipe_id": recipe.id,
        "recipe_name": recipe.name,
        "health_score": nutrition["health_score"],
        "warnings": nutrition["warnings"],
        "allergens": nutrition["allergens"],
        "ai_analysis": ai_response,
    }