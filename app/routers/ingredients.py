from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])

@router.post("/", response_model=schemas.IngredientOut, status_code=201)
def create_ingredient(
    ingredient: schemas.IngredientCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new ingredient (authenticated users only)."""
    if db.query(models.Ingredient).filter(models.Ingredient.name == ingredient.name).first():
        raise HTTPException(status_code=400, detail="Ingredient already exists")
    new_ingredient = models.Ingredient(**ingredient.model_dump())
    db.add(new_ingredient)
    db.commit()
    db.refresh(new_ingredient)
    return new_ingredient

@router.get("/", response_model=List[schemas.IngredientOut])
def get_ingredients(
    skip: int = 0,
    limit: int = Query(default=20, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve a paginated list of ingredients with optional search."""
    query = db.query(models.Ingredient)
    if search:
        query = query.filter(models.Ingredient.name.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()

@router.get("/{ingredient_id}", response_model=schemas.IngredientOut)
def get_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    """Retrieve a single ingredient by ID."""
    ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient

@router.put("/{ingredient_id}", response_model=schemas.IngredientOut)
def update_ingredient(
    ingredient_id: int,
    updates: schemas.IngredientUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update an existing ingredient (authenticated users only)."""
    ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(ingredient, field, value)
    db.commit()
    db.refresh(ingredient)
    return ingredient

@router.delete("/{ingredient_id}", status_code=204)
def delete_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete an ingredient by ID (authenticated users only)."""
    ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    db.delete(ingredient)
    db.commit()