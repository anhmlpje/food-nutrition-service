from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user

router = APIRouter(prefix="/recipes", tags=["Recipes"])

@router.post("/", response_model=schemas.RecipeOut, status_code=201)
def create_recipe(
    recipe: schemas.RecipeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new recipe with a list of ingredients and quantities."""
    new_recipe = models.Recipe(
        name=recipe.name,
        description=recipe.description,
        cuisine_type=recipe.cuisine_type,
        difficulty=recipe.difficulty,
        prep_time_minutes=recipe.prep_time_minutes,
        owner_id=current_user.id
    )
    # Attach ingredients with quantities via association table
    for item in recipe.ingredients:
        ingredient = db.query(models.Ingredient).filter(
            models.Ingredient.id == item.ingredient_id
        ).first()
        if not ingredient:
            raise HTTPException(
                status_code=404,
                detail=f"Ingredient ID {item.ingredient_id} not found"
            )
        new_recipe.ingredients.append(ingredient)

    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)
    return new_recipe

@router.get("/", response_model=List[schemas.RecipeOut])
def get_recipes(
    skip: int = 0,
    limit: int = Query(default=20, le=100),
    cuisine_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve a paginated list of recipes with optional filters."""
    query = db.query(models.Recipe)
    if cuisine_type:
        query = query.filter(models.Recipe.cuisine_type.ilike(f"%{cuisine_type}%"))
    if difficulty:
        query = query.filter(models.Recipe.difficulty == difficulty)
    return query.offset(skip).limit(limit).all()

@router.get("/{recipe_id}", response_model=schemas.RecipeOut)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Retrieve a single recipe by ID."""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

@router.put("/{recipe_id}", response_model=schemas.RecipeOut)
def update_recipe(
    recipe_id: int,
    updates: schemas.RecipeUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update a recipe's metadata (owner only)."""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if recipe.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorised to update this recipe")
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(recipe, field, value)
    db.commit()
    db.refresh(recipe)
    return recipe

@router.delete("/{recipe_id}", status_code=204)
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete a recipe (owner only)."""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if recipe.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorised to delete this recipe")
    db.delete(recipe)
    db.commit()