from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import users, ingredients, recipes, nutrition, allergens

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NutriTrack API",
    description="""
## NutriTrack — Nutrition & Recipe Analytics API

A data-driven REST API for tracking ingredients, building recipes, 
and analysing nutritional content using a dataset of 8,700+ foods.

### Features
- 🥦 **Ingredient management** — Full CRUD with nutritional data
- 🍽️ **Recipe builder** — Create recipes with weighted ingredients
- 📊 **Nutrition analytics** — Macros, micronutrients, health scores
- 🚨 **Allergen detection** — Automatic allergen tagging and filtering
- 🤖 **AI-powered insights** — Recipe recommendations and deep health analysis via Claude AI
- 🔐 **JWT authentication** — Secure endpoints with Bearer tokens
    """,
    version="1.0.0",
    contact={
        "name": "NutriTrack API",
        "url": "https://github.com/your-username/WEB-SERVICE-CW1",
    },
    license_info={
        "name": "MIT",
    }
)

# Allow cross-origin requests (useful for frontend or Postman testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(users.router)
app.include_router(ingredients.router)
app.include_router(recipes.router)
app.include_router(nutrition.router)
app.include_router(allergens.router)
app.include_router(ai.router)


@app.get("/", tags=["Health Check"])
def root():
    """API health check endpoint."""
    return {
        "status": "online",
        "message": "Welcome to NutriTrack API",
        "docs": "/docs",
        "version": "1.0.0"
    }