from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from app.database import get_db
from app import models
from app.utils.nutrition_calc import compute_recipe_nutrition, compute_nutrient_density_score

router = APIRouter(prefix="/nutrition", tags=["Nutrition Analytics"])


@router.get("/recipe/{recipe_id}")
def get_recipe_nutrition(recipe_id: int, db: Session = Depends(get_db)):
    """
    Compute full nutritional breakdown for a recipe.
    Returns macros, micronutrients, health score, warnings and allergens.
    """
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if not recipe.ingredients:
        raise HTTPException(status_code=400, detail="Recipe has no ingredients")

    # Build ingredient + quantity list from association table
    rows = db.execute(
        text("SELECT ingredient_id, quantity_g FROM recipe_ingredients WHERE recipe_id = :rid"),
        {"rid": recipe_id}
    ).fetchall()

    qty_map = {row[0]: row[1] for row in rows}

    ingredients_with_qty = [
        {"ingredient": ing, "quantity_g": qty_map.get(ing.id, 100.0)}
        for ing in recipe.ingredients
    ]

    result = compute_recipe_nutrition(ingredients_with_qty)

    return {
        "recipe_id": recipe.id,
        "recipe_name": recipe.name,
        "cuisine_type": recipe.cuisine_type,
        "difficulty": recipe.difficulty,
        "prep_time_minutes": recipe.prep_time_minutes,
        "nutrition": result["totals"],
        "health_score": result["health_score"],
        "warnings": result["warnings"],
        "allergens": result["allergens"],
    }


@router.get("/top-protein")
def top_protein_ingredients(
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db)
):
    """Return the top N ingredients ranked by protein content per 100g."""
    ingredients = (
        db.query(models.Ingredient)
        .order_by(models.Ingredient.protein.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "rank": i + 1,
            "id": ing.id,
            "name": ing.name,
            "protein_per_100g": ing.protein,
            "calories_per_100g": ing.calories,
            "nutrient_density_score": ing.protein / ing.calories * 100 if ing.calories > 0 else 0
        }
        for i, ing in enumerate(ingredients)
    ]


@router.get("/top-caffeine")
def top_caffeine_ingredients(
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db)
):
    """Return the top N ingredients ranked by caffeine content per 100g."""
    ingredients = (
        db.query(models.Ingredient)
        .filter(models.Ingredient.caffeine > 0)
        .order_by(models.Ingredient.caffeine.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "rank": i + 1,
            "id": ing.id,
            "name": ing.name,
            "caffeine_mg_per_100g": ing.caffeine,
        }
        for i, ing in enumerate(ingredients)
    ]


@router.get("/low-calorie-recipes")
def low_calorie_recipes(
    max_calories: float = Query(default=500.0),
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db)
):
    """
    Return recipes whose total calorie count falls below a given threshold.
    Calories are computed dynamically from ingredients and quantities.
    """
    recipes = db.query(models.Recipe).all()
    results = []

    for recipe in recipes:
        if not recipe.ingredients:
            continue

        rows = db.execute(
            text("SELECT ingredient_id, quantity_g FROM recipe_ingredients WHERE recipe_id = :rid"),
            {"rid": recipe.id}
        ).fetchall()

        qty_map = {row[0]: row[1] for row in rows}
        total_calories = sum(
            (ing.calories or 0) * qty_map.get(ing.id, 100.0) / 100
            for ing in recipe.ingredients
        )

        if total_calories <= max_calories:
            results.append({
                "id": recipe.id,
                "name": recipe.name,
                "cuisine_type": recipe.cuisine_type,
                "difficulty": recipe.difficulty,
                "total_calories": round(total_calories, 1),
            })

    results.sort(key=lambda x: x["total_calories"])
    return results[:limit]


@router.get("/compare")
def compare_ingredients(
    id1: int = Query(..., description="First ingredient ID"),
    id2: int = Query(..., description="Second ingredient ID"),
    db: Session = Depends(get_db)
):
    """
    Compare nutritional profiles of two ingredients side by side.
    Returns absolute values and percentage differences.
    """
    ing1 = db.query(models.Ingredient).filter(models.Ingredient.id == id1).first()
    ing2 = db.query(models.Ingredient).filter(models.Ingredient.id == id2).first()

    if not ing1:
        raise HTTPException(status_code=404, detail=f"Ingredient ID {id1} not found")
    if not ing2:
        raise HTTPException(status_code=404, detail=f"Ingredient ID {id2} not found")

    fields = ["calories", "protein", "carbohydrate", "fat", "fiber",
              "sugars", "sodium", "calcium", "potassium", "vitamin_c", "iron"]

    comparison = {}
    for field in fields:
        v1 = getattr(ing1, field) or 0.0
        v2 = getattr(ing2, field) or 0.0
        diff_pct = ((v2 - v1) / v1 * 100) if v1 > 0 else None
        comparison[field] = {
            ing1.name: v1,
            ing2.name: v2,
            "difference_pct": round(diff_pct, 1) if diff_pct is not None else "N/A"
        }

    return {
        "ingredient_1": {"id": ing1.id, "name": ing1.name},
        "ingredient_2": {"id": ing2.id, "name": ing2.name},
        "comparison_per_100g": comparison,
    }

@router.get("/top-nutrient-density")
def top_nutrient_density(
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db)
):
    """
    Return the top N ingredients ranked by nutrient density score (0-100).
    The score rewards high protein, fibre, vitamins and minerals,
    while penalising excess sugar, sodium and cholesterol.
    Based on NHS daily reference values.
    """
    ingredients = db.query(models.Ingredient).all()

    scored = []
    for ing in ingredients:
        score = compute_nutrient_density_score(ing)
        if score > 0:
            scored.append({
                "rank": 0,
                "id": ing.id,
                "name": ing.name,
                "nutrient_density_score": score,
                "calories_per_100g": ing.calories,
                "protein_per_100g": ing.protein,
                "fiber_per_100g": ing.fiber,
                "vitamin_c_per_100g": ing.vitamin_c,
                "iron_per_100g": ing.iron,
            })

    scored.sort(key=lambda x: x["nutrient_density_score"], reverse=True)
    scored = scored[:limit]
    for i, item in enumerate(scored):
        item["rank"] = i + 1

    return scored