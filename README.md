# NutriTrack API

A data-driven RESTful API for nutritional analysis and recipe management, built with FastAPI and SQLite. Backed by a dataset of 8,700+ real food items sourced from the USDA nutritional database.

## Features

- 🥦 **Ingredient Management** — Full CRUD with detailed nutritional data per 100g
- 🍽️ **Recipe Builder** — Create recipes with weighted ingredients and automatic nutrition calculation
- 📊 **Nutrition Analytics** — Macronutrients, micronutrients, health scores, and dietary warnings
- 🚨 **Allergen Detection** — Automatic allergen tagging and allergen-free ingredient filtering
- 🤖 **AI-Powered Insights** — Recipe recommendations and deep health analysis via Claude AI
- 🔐 **JWT Authentication** — Secure endpoints with Bearer token authentication

## Tech Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Framework | FastAPI | Automatic Swagger docs, async support, high performance |
| Database | SQLite + SQLAlchemy | Zero-config, file-based, ideal for local development |
| Authentication | JWT (python-jose) | Industry standard, stateless, scalable |
| Password Hashing | passlib + bcrypt | Secure one-way hashing |
| Testing | pytest + httpx | Comprehensive test coverage |
| Dataset | USDA Nutritional Database (via Kaggle) | 8,789 real food items with 77 nutritional fields |

## Project Structure
```
Web-Service-CW1/
├── app/
│   ├── main.py              # FastAPI entry point and router registration
│   ├── database.py          # SQLAlchemy engine and session management
│   ├── models.py            # Database models (User, Ingredient, Recipe)
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── auth.py              # JWT authentication logic
│   ├── routers/
│   │   ├── users.py         # User registration and login
│   │   ├── ingredients.py   # Ingredient CRUD endpoints
│   │   ├── recipes.py       # Recipe CRUD endpoints
│   │   ├── nutrition.py     # Nutrition analytics endpoints
│   │   ├── allergens.py     # Allergen detection endpoints
│   │   └── ai.py            # AI-powered recommendation endpoints
│   └── utils/
│       └── nutrition_calc.py  # Nutrition calculation and scoring logic
├── data/
│   └── nutrition.csv        # USDA nutritional dataset (8,789 items)
├── scripts/
│   └── seed_db.py           # Database seeding script
├── tests/
│   ├── test_ingredients.py  # Ingredient CRUD tests
│   ├── test_recipes.py      # Recipe CRUD and permission tests
│   └── test_nutrition.py    # Nutrition analytics tests
├── requirements.txt
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.11+
- Conda (recommended) or pip

### 1. Clone the repository
```bash
git clone https://github.com/your-username/WEB-SERVICE-CW1.git
cd WEB-SERVICE-CW1
```

### 2. Create and activate environment
```bash
conda create -n nutritrack python=3.11
conda activate nutritrack
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Seed the database
```bash
python scripts/seed_db.py
```

### 5. Start the server
```bash
python -m uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

## API Documentation

Interactive Swagger UI documentation is available at:
**`http://127.0.0.1:8000/docs`**

A PDF version of the API documentation is available here: [API Documentation](./api_docs.pdf)

## API Endpoints Overview

### Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/users/register` | Register a new user | No |
| POST | `/users/login` | Login and get JWT token | No |
| GET | `/users/me` | Get current user profile | Yes |

### Ingredients
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/ingredients/` | Create ingredient | Yes |
| GET | `/ingredients/` | List ingredients (search + pagination) | No |
| GET | `/ingredients/{id}` | Get ingredient by ID | No |
| PUT | `/ingredients/{id}` | Update ingredient | Yes |
| DELETE | `/ingredients/{id}` | Delete ingredient | Yes |

### Recipes
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/recipes/` | Create recipe | Yes |
| GET | `/recipes/` | List recipes (filter + pagination) | No |
| GET | `/recipes/{id}` | Get recipe by ID | No |
| PUT | `/recipes/{id}` | Update recipe (owner only) | Yes |
| DELETE | `/recipes/{id}` | Delete recipe (owner only) | Yes |

### Nutrition Analytics
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/nutrition/recipe/{id}` | Full nutrition breakdown + health score | No |
| GET | `/nutrition/top-protein` | Top ingredients by protein | No |
| GET | `/nutrition/top-caffeine` | Top ingredients by caffeine | No |
| GET | `/nutrition/low-calorie-recipes` | Recipes below calorie threshold | No |
| GET | `/nutrition/compare` | Side-by-side ingredient comparison | No |

### Allergens
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/allergens/ingredient/{id}` | Get allergens for an ingredient | No |
| GET | `/allergens/recipe/{id}` | Get allergen report for a recipe | No |
| GET | `/allergens/free` | Find allergen-free ingredients | No |

### AI-Powered Analytics
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/ai/recommend` | AI recipe recommendations | Yes |
| POST | `/ai/analyse` | AI deep health analysis | Yes |

## Running Tests
```bash
python -m pytest tests/ -v
```

Expected output: **31 passed**

## Environment Variables

For AI endpoints, set your Anthropic API key:
```bash
# Windows
set ANTHROPIC_API_KEY=your_api_key_here

# Mac/Linux
export ANTHROPIC_API_KEY=your_api_key_here
```

## Data Source

Nutritional data sourced from the **USDA FoodData Central** database, accessed via Kaggle:
- Dataset: [Nutritional Values for Common Foods and Products](https://www.kaggle.com/datasets/trolukovich/nutritional-values-for-common-foods-and-products)
- 8,789 food items with 77 nutritional attributes
- All values expressed per 100g serving

## Generative AI Declaration

This project was developed with the assistance of Claude AI (Anthropic). See the technical report for full details of AI usage, including conversation logs and a reflective analysis of how GenAI was used throughout the development process.