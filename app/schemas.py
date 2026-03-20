from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str
    password: str = Field(min_length=1, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Username cannot be blank")
        return value


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str


class IngredientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    serving_size: Optional[str] = "100 g"
    calories: Optional[float] = Field(default=0.0, ge=0)
    protein: Optional[float] = Field(default=0.0, ge=0)
    carbohydrate: Optional[float] = Field(default=0.0, ge=0)
    fat: Optional[float] = Field(default=0.0, ge=0)
    fiber: Optional[float] = Field(default=0.0, ge=0)
    sugars: Optional[float] = Field(default=0.0, ge=0)
    sodium: Optional[float] = Field(default=0.0, ge=0)
    calcium: Optional[float] = Field(default=0.0, ge=0)
    potassium: Optional[float] = Field(default=0.0, ge=0)
    vitamin_c: Optional[float] = Field(default=0.0, ge=0)
    vitamin_a: Optional[float] = Field(default=0.0, ge=0)
    iron: Optional[float] = Field(default=0.0, ge=0)
    caffeine: Optional[float] = Field(default=0.0, ge=0)
    water: Optional[float] = Field(default=0.0, ge=0)
    cholesterol: Optional[float] = Field(default=0.0, ge=0)
    alcohol: Optional[float] = Field(default=0.0, ge=0)
    allergens: Optional[str] = ""

    @field_validator("name", "serving_size")
    @classmethod
    def validate_non_blank_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be blank")
        return value


class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    calories: Optional[float] = Field(default=None, ge=0)
    protein: Optional[float] = Field(default=None, ge=0)
    carbohydrate: Optional[float] = Field(default=None, ge=0)
    fat: Optional[float] = Field(default=None, ge=0)
    fiber: Optional[float] = Field(default=None, ge=0)
    sugars: Optional[float] = Field(default=None, ge=0)
    sodium: Optional[float] = Field(default=None, ge=0)
    calcium: Optional[float] = Field(default=None, ge=0)
    potassium: Optional[float] = Field(default=None, ge=0)
    vitamin_c: Optional[float] = Field(default=None, ge=0)
    vitamin_a: Optional[float] = Field(default=None, ge=0)
    iron: Optional[float] = Field(default=None, ge=0)
    caffeine: Optional[float] = Field(default=None, ge=0)
    water: Optional[float] = Field(default=None, ge=0)
    cholesterol: Optional[float] = Field(default=None, ge=0)
    alcohol: Optional[float] = Field(default=None, ge=0)
    allergens: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_optional_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be blank")
        return value


class IngredientOut(IngredientCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class RecipeIngredientInput(BaseModel):
    ingredient_id: int = Field(gt=0)
    quantity_g: float = Field(gt=0)


class RecipeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = ""
    cuisine_type: Optional[str] = None
    difficulty: Optional[Literal["easy", "medium", "hard"]] = "medium"
    prep_time_minutes: Optional[int] = Field(default=0, ge=0)
    ingredients: List[RecipeIngredientInput] = Field(default_factory=list)

    @field_validator("name", "description", "cuisine_type")
    @classmethod
    def validate_recipe_text_fields(cls, value: Optional[str], info) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if info.field_name == "name" and not value:
            raise ValueError("Name cannot be blank")
        return value


class RecipeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cuisine_type: Optional[str] = None
    difficulty: Optional[Literal["easy", "medium", "hard"]] = None
    prep_time_minutes: Optional[int] = Field(default=None, ge=0)

    @field_validator("name", "description", "cuisine_type")
    @classmethod
    def validate_optional_recipe_text_fields(cls, value: Optional[str], info) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if info.field_name == "name" and not value:
            raise ValueError("Name cannot be blank")
        return value


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


class NutritionSummary(BaseModel):
    recipe_id: int
    recipe_name: str
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    total_fiber_g: float
    total_sodium_mg: float
    health_score: float
    warnings: List[str]
