from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ─── User ────────────────────────────────────────────────
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str

# ─── Ingredient ──────────────────────────────────────────
class IngredientCreate(BaseModel):
    name: str
    serving_size: Optional[str] = "100 g"
    calories: Optional[float] = 0.0
    protein: Optional[float] = 0.0
    carbohydrate: Optional[float] = 0.0
    fat: Optional[float] = 0.0
    fiber: Optional[float] = 0.0
    sugars: Optional[float] = 0.0
    sodium: Optional[float] = 0.0
    calcium: Optional[float] = 0.0
    potassium: Optional[float] = 0.0
    vitamin_c: Optional[float] = 0.0
    vitamin_a: Optional[float] = 0.0
    iron: Optional[float] = 0.0
    caffeine: Optional[float] = 0.0
    water: Optional[float] = 0.0
    cholesterol: Optional[float] = 0.0
    alcohol: Optional[float] = 0.0
    allergens: Optional[str] = ""  # Comma-separated list of allergens, e.g. "gluten,dairy"

class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbohydrate: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None
    sugars: Optional[float] = None
    sodium: Optional[float] = None
    calcium: Optional[float] = None
    potassium: Optional[float] = None
    vitamin_c: Optional[float] = None
    vitamin_a: Optional[float] = None
    iron: Optional[float] = None
    caffeine: Optional[float] = None
    water: Optional[float] = None
    cholesterol: Optional[float] = None
    alcohol: Optional[float] = None
    allergens: Optional[str] = None  # Allow clearing allergens by setting to empty string

class IngredientOut(IngredientCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}

# ─── Recipe ──────────────────────────────────────────────
class RecipeIngredientInput(BaseModel):
    ingredient_id: int
    quantity_g: float

class RecipeCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    cuisine_type: Optional[str] = None
    difficulty: Optional[str] = "medium"
    prep_time_minutes: Optional[int] = 0
    ingredients: List[RecipeIngredientInput] = []

class RecipeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cuisine_type: Optional[str] = None
    difficulty: Optional[str] = None
    prep_time_minutes: Optional[int] = None

class RecipeOut(BaseModel):
    id: int
    name: str
    description: str
    cuisine_type: Optional[str]
    difficulty: str
    prep_time_minutes: int
    owner_id: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}

# ─── Nutrition Analysis ──────────────────────────────────
class NutritionSummary(BaseModel):
    recipe_id: int
    recipe_name: str
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    total_fiber_g: float
    total_sodium_mg: float
    health_score: float  # Computed score from 0 to 100
    warnings: List[str]  # e.g. "High sodium", "High sugar"