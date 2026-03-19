from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.utils.nutrition_calc import infer_allergens, ALLERGEN_KEYWORDS

router = APIRouter(prefix="/allergens", tags=["Allergens"])

SUPPORTED_ALLERGENS = list(ALLERGEN_KEYWORDS.keys())


@router.get("/ingredient/{ingredient_id}")
def get_ingredient_allergens(ingredient_id: int, db: Session = Depends(get_db)):
    """Return detected allergens for a specific ingredient."""
    ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    allergens = ingredient.allergens.split(",") if ingredient.allergens else []
    allergens = [a.strip() for a in allergens if a.strip()]

    return {
        "ingredient_id": ingredient.id,
        "ingredient_name": ingredient.name,
        "allergens": allergens,
        "allergen_free": len(allergens) == 0,
    }


@router.get("/recipe/{recipe_id}")
def get_recipe_allergens(recipe_id: int, db: Session = Depends(get_db)):
    """
    Return a full allergen report for a recipe.
    Lists all detected allergens and which ingredients trigger them.
    """
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    allergen_map = {}

    for ingredient in recipe.ingredients:
        allergens = ingredient.allergens.split(",") if ingredient.allergens else []
        for allergen in allergens:
            allergen = allergen.strip()
            if allergen:
                if allergen not in allergen_map:
                    allergen_map[allergen] = []
                allergen_map[allergen].append(ingredient.name)

    return {
        "recipe_id": recipe.id,
        "recipe_name": recipe.name,
        "total_allergens_detected": len(allergen_map),
        "allergen_report": allergen_map,
        "safe_for_allergies": len(allergen_map) == 0,
    }


@router.get("/free")
def allergen_free_ingredients(
    exclude: str = Query(..., description=f"Allergen to exclude. Supported: {', '.join(ALLERGEN_KEYWORDS.keys())}"),
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db)
):
    """
    Return ingredients that do not contain a specified allergen.
    Useful for users with dietary restrictions.
    """
    if exclude not in SUPPORTED_ALLERGENS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported allergen. Choose from: {', '.join(SUPPORTED_ALLERGENS)}"
        )

    ingredients = (
        db.query(models.Ingredient)
        .filter(
            ~models.Ingredient.allergens.contains(exclude)
        )
        .limit(limit)
        .all()
    )

    return {
        "allergen_excluded": exclude,
        "count": len(ingredients),
        "ingredients": [
            {"id": ing.id, "name": ing.name, "calories": ing.calories}
            for ing in ingredients
        ]
    }