from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Many-to-many association table between recipes and ingredients
recipe_ingredients = Table(
    "recipe_ingredients",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id"), primary_key=True),
    Column("ingredient_id", Integer, ForeignKey("ingredients.id"), primary_key=True),
    Column("quantity_g", Float, nullable=False)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    recipes = relationship("Recipe", back_populates="owner")

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    serving_size = Column(String, default="100 g")

    # Core macronutrients (per 100g)
    calories = Column(Float, default=0.0)
    protein = Column(Float, default=0.0)
    carbohydrate = Column(Float, default=0.0)
    fat = Column(Float, default=0.0)
    fiber = Column(Float, default=0.0)
    sugars = Column(Float, default=0.0)

    # Micronutrients
    sodium = Column(Float, default=0.0)
    calcium = Column(Float, default=0.0)
    potassium = Column(Float, default=0.0)
    vitamin_c = Column(Float, default=0.0)
    vitamin_a = Column(Float, default=0.0)
    iron = Column(Float, default=0.0)

    # Special fields for advanced analytics
    caffeine = Column(Float, default=0.0)
    water = Column(Float, default=0.0)
    cholesterol = Column(Float, default=0.0)
    alcohol = Column(Float, default=0.0)

    # Allergens stored as comma-separated string e.g. "gluten,dairy,nuts"
    allergens = Column(String, default="")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    recipes = relationship("Recipe", secondary=recipe_ingredients, back_populates="ingredients")

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, default="")
    cuisine_type = Column(String, index=True)
    difficulty = Column(String, default="medium")  # easy / medium / hard
    prep_time_minutes = Column(Integer, default=0)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="recipes")
    ingredients = relationship("Ingredient", secondary=recipe_ingredients, back_populates="recipes")