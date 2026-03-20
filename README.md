# NutriTrack API

A data-driven RESTful API for nutritional analysis and recipe management, built with FastAPI and SQLite. Backed by a dataset of 8,789 real food items sourced from the USDA nutritional database.

## Live Deployment

**Base URL:** `https://nutritrack-api-1m8s.onrender.com`  
**API Documentation:** `https://nutritrack-api-1m8s.onrender.com/docs`

## Features

- 🥦 **Ingredient Management** — Full CRUD with detailed nutritional data per 100g
- 🍽️ **Recipe Builder** — Create recipes with weighted ingredients and automatic nutrition calculation
- 📊 **Nutrition Analytics** — Macronutrients, micronutrients, health scores, and dietary warnings
- 🚨 **Allergen Detection** — Automatic allergen inference engine with allergen-free filtering
- 🤖 **MCP Server** — 8 tools exposing nutritional data directly to AI assistants via Model Context Protocol
- 🔐 **JWT Authentication** — Secure endpoints with Bearer token authentication
- 🛡️ **Rate Limiting** — Protection against brute force attacks (5 req/min on register, 10 req/min on login)
- 🔑 **Password Validation** — Enforced password strength (8+ chars, uppercase, digit)

## Tech Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Framework | FastAPI | Automatic Swagger docs, async support, high performance |
| Database | SQLite + SQLAlchemy | Zero-config, file-based, ideal for local development |
| Authentication | JWT (python-jose) | Industry standard, stateless, scalable |
| Password Hashing | passlib + bcrypt | Secure one-way hashing |
| Rate Limiting | slowapi | Lightweight, FastAPI-compatible rate limiting |
| Testing | pytest + httpx | Comprehensive test coverage with isolated test database |
| MCP | mcp | Model Context Protocol for AI assistant integration |
| Deployment | Render | Automatic CI/CD via GitHub webhooks |
| Dataset | USDA FoodData Central (via Kaggle) | 8,789 real food items with 77 nutritional fields |

## Project Structure

```
WEB-SERVICE-CW1/
├── app/
│   ├── main.py              # FastAPI entry point and router registration
│   ├── database.py          # SQLAlchemy engine and session management
│   ├── models.py            # Database models (User, Ingredient, Recipe)
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── auth.py              # JWT authentication logic
│   ├── limiter.py           # Rate limiter instance
│   ├── routers/
│   │   ├── users.py         # User registration and login
│   │   ├── ingredients.py   # Ingredient CRUD endpoints
│   │   ├── recipes.py       # Recipe CRUD endpoints
│   │   ├── nutrition.py     # Nutrition analytics endpoints
│   │   └── allergens.py     # Allergen detection endpoints
│   └── utils/
│       └── nutrition_calc.py  # Nutrition calculation, health scoring and allergen inference
├── data/
│   └── nutrition.csv        # USDA nutritional dataset (8,789 items)
├── scripts/
│   ├── seed_db.py           # Database seeding script
│   └── test_mcp.py          # MCP server demonstration script
├── tests/
│   ├── conftest.py          # Shared test fixtures and rate limit reset
│   ├── test_allergens.py    # Allergen endpoint tests
│   ├── test_ingredients.py  # Ingredient CRUD and password validation tests
│   ├── test_recipes.py      # Recipe CRUD and permission tests
│   └── test_nutrition.py    # Nutrition analytics tests
├── mcp_server.py            # MCP server exposing 8 nutrition tools
├── Procfile                 # Render deployment configuration
├── runtime.txt              # Python version specification
├── api_docs.pdf             # API documentation (exported from Swagger UI)
├── requirements.txt
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.11+
- Conda (recommended) or pip

### 1. Clone the repository
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
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
Expected output: `Done! Inserted 8789 ingredients, skipped 0.`

### 5. Start the server
```bash
python -m uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

### Password Requirements
When registering, passwords must:
- Be at least 8 characters long
- Contain at least one uppercase letter
- Contain at least one digit

## API Documentation

Interactive Swagger UI documentation is available at:
- **Local:** `http://127.0.0.1:8000/docs`
- **Live:** `https://nutritrack-api-1m8s.onrender.com/docs`

A PDF version of the API documentation is available here: [API Documentation](./api_docs.pdf)

## API Endpoints Overview

### Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/users/register` | Register a new user (rate limited: 5/min) | No |
| POST | `/users/login` | Login and get JWT token (rate limited: 10/min) | No |
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
| POST | `/recipes/` | Create recipe with weighted ingredients | Yes |
| GET | `/recipes/` | List recipes (filter + pagination) | No |
| GET | `/recipes/{id}` | Get recipe by ID | No |
| PUT | `/recipes/{id}` | Update recipe (owner only) | Yes |
| DELETE | `/recipes/{id}` | Delete recipe (owner only) | Yes |

### Nutrition Analytics
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/nutrition/recipe/{id}` | Full nutrition breakdown + health score + warnings | No |
| GET | `/nutrition/top-protein` | Top ingredients by protein content | No |
| GET | `/nutrition/top-caffeine` | Top ingredients by caffeine content | No |
| GET | `/nutrition/low-calorie-recipes` | Recipes below calorie threshold | No |
| GET | `/nutrition/compare` | Side-by-side ingredient comparison | No |
| GET | `/nutrition/top-nutrient-density` | Top ingredients by nutrient density score (0-100) | No |

### Allergens
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/allergens/ingredient/{id}` | Get allergens for an ingredient | No |
| GET | `/allergens/recipe/{id}` | Get full allergen report for a recipe | No |
| GET | `/allergens/free` | Find ingredients free from a specified allergen | No |

## MCP Server

NutriTrack exposes an MCP (Model Context Protocol) server, allowing AI assistants such as Claude to directly query nutritional data in natural language.

### Available Tools (8)

| Tool | Description |
|------|-------------|
| `search_ingredients` | Search ingredients by name with full nutritional data |
| `get_top_protein_ingredients` | Ranked list by protein content per 100g |
| `get_top_caffeine_ingredients` | Ranked list by caffeine content per 100g |
| `get_top_nutrient_density` | Ranked list by custom nutrient density score (0-100) |
| `check_ingredient_allergens` | Detect allergens in a specific ingredient |
| `find_allergen_free_ingredients` | Filter ingredients by allergen exclusion |
| `compare_ingredients` | Side-by-side nutritional comparison of two ingredients |
| `analyse_recipe_nutrition` | Full nutrition analysis for a custom recipe |

### Claude Desktop Integration

Add this to your Claude Desktop config file:

**Windows path:** `C:\Users\<username>\AppData\Local\Packages\Claude_*\LocalCache\Roaming\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "nutritrack": {
      "command": "C:\\path\\to\\conda\\envs\\nutritrack\\python.exe",
      "args": ["C:\\path\\to\\WEB-SERVICE-CW1\\mcp_server.py"]
    }
  }
}
```

### Test MCP Tools Locally
```bash
python scripts/test_mcp.py
```

## Running Tests

```bash
python -m pytest tests/ -v
```

Expected output: **45 passed**

Test coverage includes:
- Ingredient CRUD, search, pagination
- Recipe CRUD, ownership enforcement (403 on unauthorised)
- Password strength validation
- Nutrition calculation accuracy
- Allergen detection and aggregation
- Nutrient density scoring

## Deployment

NutriTrack is deployed on **Render** with automatic CI/CD via GitHub webhooks. Every `git push` to the `main` branch triggers a new deployment automatically.

- **Live URL:** `https://nutritrack-api-1m8s.onrender.com`
- **Platform:** Render (Free tier)
- **Auto-deploy:** Enabled via GitHub webhook

## Data Source

Nutritional data sourced from the **USDA FoodData Central** database, accessed via Kaggle:
- **Dataset:** [Nutritional Values for Common Foods and Products](https://www.kaggle.com/datasets/trolukovich/nutritional-values-for-common-foods-and-products)
- **Size:** 8,789 food items with 77 nutritional attributes
- **Values:** All expressed per 100g serving
- **License:** Public domain, suitable for academic use

## Novel Features

- **Allergen Inference Engine** — Automatically detects allergens from ingredient names using keyword matching, without requiring a separate allergen dataset. Applied to all 8,789 items at import time.
- **Health Score Algorithm** — Computes a 0-100 health score per recipe based on NHS daily reference values, rewarding protein and fibre while penalising excess sodium, sugar and fat.
- **Nutrient Density Score** — Custom scoring algorithm combining 6 positive nutrients (protein, fibre, vitamin C, calcium, potassium, iron) against 3 negative ones (sugar, sodium, cholesterol).
- **MCP Integration** — Exposes the entire nutritional database to AI assistants via the Model Context Protocol, enabling natural language queries.

## Generative AI Declaration

This project was developed with the assistance of Claude AI (Anthropic). See the technical report for full details of AI usage, including conversation logs and a reflective analysis of how GenAI was used throughout the development process.