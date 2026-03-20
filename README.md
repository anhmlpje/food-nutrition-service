# NutriTrack API

A data-driven RESTful API for nutritional analysis and recipe management, built with FastAPI and SQLite.
Backed by a dataset of 8,789 real food items sourced from the USDA FoodData Central database.

---

## Live Links

| Resource | URL |
|----------|-----|
| **Frontend Dashboard** | https://anhmlpje.github.io/food-nutrition-service/ |
| **API Base URL** | https://nutritrack-api-1m8s.onrender.com |
| **Swagger UI Docs** | https://nutritrack-api-1m8s.onrender.com/docs |
| **GitHub Repository** | https://github.com/anhmlpje/food-nutrition-service |

---

## Features

- 🥦 **Ingredient Management** — Full CRUD with detailed nutritional data per 100g
- 🍽️ **Recipe Builder** — Create recipes with weighted ingredients and automatic nutrition calculation
- 📊 **Nutrition Analytics** — Macronutrients, micronutrients, health scores, and dietary warnings
- 🚨 **Allergen Detection** — Automatic allergen inference engine with allergen-free filtering
- 🤖 **MCP Server** — 8 tools exposing nutritional data directly to AI assistants via Model Context Protocol
- 🔐 **JWT Authentication** — Secure endpoints with Bearer token authentication
- 🛡️ **Rate Limiting** — Protection against brute force attacks (5 req/min on register, 10 req/min on login)
- 🔑 **Password Validation** — Enforced password strength (8+ characters, uppercase letter, digit)
- 🌐 **Vue.js Frontend** — Interactive dashboard with Chart.js visualisations, hosted on GitHub Pages

---

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
| Frontend | Vue.js 3 + Chart.js | Reactive single-page app with data visualisations |
| API Deployment | Render | Automatic CI/CD via GitHub webhooks |
| Frontend Hosting | GitHub Pages | Static site hosting, free and automatic |
| Dataset | USDA FoodData Central (via Kaggle) | 8,789 real food items with 77 nutritional fields |

---

## Project Structure

```
food-nutrition-service/
├── app/
│   ├── main.py                  # FastAPI entry point and router registration
│   ├── database.py              # SQLAlchemy engine and session management
│   ├── models.py                # Database models (User, Ingredient, Recipe)
│   ├── schemas.py               # Pydantic request/response schemas
│   ├── auth.py                  # JWT authentication logic
│   ├── limiter.py               # Rate limiter instance (shared across routers)
│   ├── routers/
│   │   ├── users.py             # User registration and login
│   │   ├── ingredients.py       # Ingredient CRUD endpoints
│   │   ├── recipes.py           # Recipe CRUD endpoints
│   │   ├── nutrition.py         # Nutrition analytics endpoints
│   │   └── allergens.py         # Allergen detection endpoints
│   └── utils/
│       └── nutrition_calc.py    # Nutrition calculation, health scoring, allergen inference
├── data/
│   └── nutrition.csv            # USDA nutritional dataset (8,789 items)
├── scripts/
│   ├── seed_db.py               # One-time database seeding script
│   └── test_mcp.py              # MCP server tool demonstration script
├── tests/
│   ├── conftest.py              # Shared fixtures and rate limit reset
│   ├── test_allergens.py        # Allergen endpoint tests (7 tests)
│   ├── test_ingredients.py      # Ingredient CRUD and password validation tests (17 tests)
│   ├── test_recipes.py          # Recipe CRUD and ownership permission tests (10 tests)
│   └── test_nutrition.py        # Nutrition analytics and scoring tests (11 tests)
├── mcp_server.py                # MCP server exposing 8 nutrition tools to AI assistants
├── index.html                   # Vue.js frontend dashboard (served via GitHub Pages)
├── Procfile                     # Render deployment start command
├── runtime.txt                  # Python version specification for Render
├── api_docs.pdf                 # API documentation exported from Swagger UI
├── requirements.txt
└── README.md
```

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- Conda (recommended) or pip

### 1. Clone the repository
```bash
git clone https://github.com/anhmlpje/food-nutrition-service.git
cd food-nutrition-service
```

### 2. Create and activate environment

**Option A: Using Conda (recommended)**
```bash
conda create -n nutritrack python=3.11
conda activate nutritrack
```

**Option B: Using venv**
```bash
python -m venv nutritrack

# Windows
nutritrack\Scripts\activate

# Mac/Linux
source nutritrack/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Seed the database
```bash
python scripts/seed_db.py
```

Expected output:
```
Seeding database from nutrition.csv ...
  Inserted 500 ingredients...
  ...
Done! Inserted 8789 ingredients, skipped 0.
```

### 5. Start the server
```bash
python -m uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`
Swagger UI will be available at `http://127.0.0.1:8000/docs`

### Password Requirements

When registering, passwords must:
- Be at least 8 characters long
- Contain at least one uppercase letter
- Contain at least one digit

---

## Frontend Dashboard

NutriTrack includes a Vue.js frontend dashboard hosted on GitHub Pages.

**Live:** https://anhmlpje.github.io/food-nutrition-service/

The frontend uses smart API detection — it automatically connects to the local API
(`http://127.0.0.1:8000`) when opened locally or from `file://`, and the live Render
deployment when accessed via GitHub Pages. You can also override the target by appending
`?api=http://your-url` to the URL.

| Page | Features |
|------|----------|
| 🏠 Home | Stats overview, quick search, top protein and nutrient density charts |
| 🔍 Search | Real-time ingredient search with calorie comparison bar chart |
| ↑ Rankings | Protein / caffeine / nutrient density leaderboards with bar charts |
| ⇌ Compare | Side-by-side ingredient comparison with radar chart |
| ⚠ Allergens | Filter ingredients by allergen exclusion |
| ✎ Builder | Register or login, build a recipe, submit via API, auto-analyse nutrition |
| ✦ Analyser | Full nutritional breakdown with doughnut chart, bar chart and health score |

---

## Usage Examples

### 1. Register and login
```bash
# Register a new account
curl -X POST https://nutritrack-api-1m8s.onrender.com/users/register \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "Password123"}'

# Login and copy the access_token from the response
curl -X POST https://nutritrack-api-1m8s.onrender.com/users/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john&password=Password123"
```

### 2. Search ingredients
```bash
# Search for salmon-based ingredients
curl "https://nutritrack-api-1m8s.onrender.com/ingredients/?search=salmon&limit=5"

# Get a specific ingredient by ID
curl https://nutritrack-api-1m8s.onrender.com/ingredients/1
```

### 3. Create a recipe
```bash
curl -X POST https://nutritrack-api-1m8s.onrender.com/recipes/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Grilled Salmon with Spinach",
    "cuisine_type": "Mediterranean",
    "difficulty": "easy",
    "prep_time_minutes": 20,
    "ingredients": [
      {"ingredient_id": 3, "quantity_g": 150},
      {"ingredient_id": 6, "quantity_g": 80}
    ]
  }'
```

### 4. Analyse recipe nutrition
```bash
# Returns macros, health score (0-100), warnings and allergens
curl https://nutritrack-api-1m8s.onrender.com/nutrition/recipe/1
```

### 5. Explore analytics
```bash
# Top 10 high-protein ingredients
curl "https://nutritrack-api-1m8s.onrender.com/nutrition/top-protein?limit=10"

# Top ingredients by custom nutrient density score (0-100)
curl "https://nutritrack-api-1m8s.onrender.com/nutrition/top-nutrient-density?limit=10"

# Compare two ingredients side by side
curl "https://nutritrack-api-1m8s.onrender.com/nutrition/compare?id1=2&id2=3"

# Find gluten-free ingredients
curl "https://nutritrack-api-1m8s.onrender.com/allergens/free?exclude=gluten&limit=20"
```

---

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

---

## API Documentation

Interactive Swagger UI documentation is available at:
- **Local:** `http://127.0.0.1:8000/docs`
- **Live:** `https://nutritrack-api-1m8s.onrender.com/docs`

A PDF version of the full API documentation is included in the repository: [api_docs.pdf](./api_docs.pdf)

---

## MCP Server

NutriTrack exposes an MCP (Model Context Protocol) server, allowing AI assistants such as Claude
to directly query nutritional data in natural language without making manual REST API calls.

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

### Running the MCP Server
```bash
python mcp_server.py
```

### Test all 8 MCP tools
```bash
python scripts/test_mcp.py
```

### Claude Desktop Integration

Add the `mcpServers` section to your existing Claude Desktop config file:

**Windows config path:**
`C:\Users\<username>\AppData\Local\Packages\Claude_*\LocalCache\Roaming\Claude\claude_desktop_config.json`

**Option A: Using Conda**
```json
{
  "mcpServers": {
    "nutritrack": {
      "command": "C:\\Users\\<username>\\anaconda3\\envs\\nutritrack\\python.exe",
      "args": ["C:\\path\\to\\food-nutrition-service\\mcp_server.py"]
    }
  }
}
```

**Option B: Using venv**
```json
{
  "mcpServers": {
    "nutritrack": {
      "command": "C:\\path\\to\\food-nutrition-service\\nutritrack\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\food-nutrition-service\\mcp_server.py"]
    }
  }
}
```

> **Note:** Add only the `mcpServers` section to your existing config file — do not overwrite
> the entire file, as it may contain other Claude Desktop settings such as `preferences`.
> Replace `<username>` and `C:\\path\\to\\` with your actual values.
> Run `where python` (Windows) or `which python` (Mac/Linux) with the nutritrack
> environment activated to find your Python executable path.

---

## Running Tests

```bash
python -m pytest tests/ -v
```

Expected output: **45 passed**

| Test File | Tests | Coverage |
|-----------|-------|----------|
| test_allergens.py | 7 | Allergen queries, recipe allergen reports, allergen-free filtering |
| test_ingredients.py | 17 | CRUD operations, search, pagination, password strength validation |
| test_recipes.py | 10 | CRUD, ownership enforcement (403 on unauthorised access) |
| test_nutrition.py | 11 | Calorie accuracy, health score range, ranking order, comparison |

All tests use an isolated SQLite test database and have rate limiting disabled to prevent interference.

---

## Deployment

### Backend — Render

NutriTrack is deployed on **Render** with automatic CI/CD via GitHub webhooks.
Every `git push` to the `main` branch triggers a new deployment automatically.

- **Live URL:** `https://nutritrack-api-1m8s.onrender.com`
- **Platform:** Render (Free tier)
- **Auto-deploy:** Enabled via GitHub webhook
- **Start command:** `python scripts/seed_db.py && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend — GitHub Pages

The Vue.js frontend is hosted on GitHub Pages directly from the `main` branch root.

- **Live URL:** `https://anhmlpje.github.io/food-nutrition-service/`
- **Platform:** GitHub Pages (free)
- **Auto-deploy:** Every push to `main` updates the frontend automatically

---

## Data Source

Nutritional data sourced from the **USDA FoodData Central** database, accessed via Kaggle:
- **Dataset:** [Nutritional Values for Common Foods and Products](https://www.kaggle.com/datasets/trolukovich/nutritional-values-for-common-foods-and-products)
- **Size:** 8,789 food items with 77 nutritional attributes per item
- **Values:** All expressed per 100g serving
- **License:** Public domain, suitable for academic use

---

## Novel Features

**Allergen Inference Engine** — Automatically detects 7 allergen categories (gluten, dairy, nuts, soy,
egg, fish, shellfish) from ingredient names using keyword matching, without requiring a separate
allergen dataset. Applied to all 8,789 items at import time.

**Health Score Algorithm** — Computes a 0–100 health score per recipe based on NHS daily reference
values. Rewards protein and fibre, penalises excess sodium, sugar and fat.

**Nutrient Density Score** — Custom scoring algorithm combining 6 positive nutrients (protein, fibre,
vitamin C, calcium, potassium, iron) against 3 negative ones (sugar, sodium, cholesterol) to rank
the most nutritionally valuable foods per calorie.

**MCP Integration** — Exposes the entire nutritional database to AI assistants via the Model Context
Protocol, enabling natural language queries such as "find high-protein gluten-free ingredients"
directly in Claude Desktop without any manual API calls.

**Smart Frontend API Detection** — The Vue.js frontend automatically detects whether it is running
locally (`file://` or `localhost`) or on GitHub Pages, and connects to the appropriate API endpoint.
The target can also be overridden via `?api=` URL parameter for flexibility during development.

---

## Generative AI Declaration

This project was developed with the assistance of Claude AI (Anthropic). See the technical report
for full details of AI usage, including conversation logs and a reflective analysis of how GenAI
was used throughout the development process.