# NutriTrack API

A data-driven RESTful API for nutritional analysis and recipe management, built with FastAPI and SQLite.
It is backed by a dataset of 8,789 real food items sourced from USDA FoodData Central via Kaggle.

---

## Live Links

| Resource | URL |
|----------|-----|
| Frontend Dashboard | https://anhmlpje.github.io/food-nutrition-service/ |
| API Base URL | https://nutritrack-api-1m8s.onrender.com |
| Swagger UI Docs | https://nutritrack-api-1m8s.onrender.com/docs |
| GitHub Repository | https://github.com/anhmlpje/food-nutrition-service |

---

## Features

- Ingredient Management: full CRUD with detailed nutritional data per 100g
- Recipe Builder: create recipes with weighted ingredients and automatic nutrition calculation
- Nutrition Analytics: macronutrients, micronutrients, health scores, warnings, and rankings
- Allergen Detection: automatic allergen inference engine with allergen-free filtering
- MCP Server: 8 tools exposing nutritional data to AI assistants via Model Context Protocol
- JWT Authentication: protected endpoints using Bearer tokens
- Rate Limiting: brute-force protection on registration and login
- Password Validation: minimum 8 characters, at least one uppercase letter, at least one digit
- Schema Validation: rejects invalid payloads such as negative nutrition values or invalid recipe difficulty
- Vue.js Frontend: interactive dashboard with Chart.js visualisations hosted on GitHub Pages

---

## Tech Stack

| Component | Technology | Justification |
|-----------|------------|---------------|
| Framework | FastAPI | Automatic Swagger docs, clean routing, strong developer experience |
| Database | SQLite + SQLAlchemy | Lightweight SQL persistence, good fit for local development and coursework scale |
| Authentication | JWT (`python-jose`) | Stateless token-based authentication |
| Password Hashing | `passlib` + `bcrypt` | Secure one-way password storage |
| Rate Limiting | `slowapi` | Lightweight FastAPI-compatible abuse protection |
| Testing | `pytest` + `httpx` | Automated API and smoke-test coverage |
| MCP | `mcp` | Direct AI assistant integration |
| Frontend | Vue.js 3 + Chart.js | Simple reactive dashboard with visual analytics |
| API Deployment | Render | Easy hosted deployment with auto-deploy from GitHub |
| Frontend Hosting | GitHub Pages | Free static hosting |
| Dataset | USDA FoodData Central via Kaggle | Real-world nutritional dataset with broad coverage |

---

## Project Structure

```text
food-nutrition-service/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── limiter.py
│   ├── routers/
│   │   ├── users.py
│   │   ├── ingredients.py
│   │   ├── recipes.py
│   │   ├── nutrition.py
│   │   └── allergens.py
│   └── utils/
│       └── nutrition_calc.py
├── data/
│   └── nutrition.csv
├── scripts/
│   ├── seed_db.py
│   └── test_mcp.py
├── tests/
│   ├── conftest.py
│   ├── test_allergens.py
│   ├── test_auth_and_security.py
│   ├── test_ingredients.py
│   ├── test_mcp_smoke.py
│   ├── test_nutrition.py
│   ├── test_recipes.py
│   └── test_seed_db.py
├── mcp_server.py
├── index.html
├── Procfile
├── runtime.txt
├── api_docs.pdf
├── requirements.txt
└── README.md
```

---

## Setup Instructions

### Prerequisites

- Python 3.11+
- Conda or `venv`

### 1. Clone the repository

```bash
git clone https://github.com/anhmlpje/food-nutrition-service.git
cd food-nutrition-service
```

### 2. Create and activate an environment

Conda:

```bash
conda create -n nutritrack python=3.11
conda activate nutritrack
```

venv:

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

```text
Seeding database from nutrition.csv ...
  Inserted 500 ingredients...
  ...
Done! Inserted 8789 ingredients, skipped 0.
```

### 5. Start the API

```bash
python -m uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000` and Swagger UI is available at `http://127.0.0.1:8000/docs`.

### Optional Environment Variables

The API supports environment-based configuration for safer deployment:

```bash
set NUTRITRACK_SECRET_KEY=your-production-secret
set APP_ENV=development
set NUTRITRACK_TOKEN_EXPIRE_MINUTES=30
set NUTRITRACK_ALLOWED_ORIGINS=http://127.0.0.1:8000,http://localhost:5500,https://anhmlpje.github.io
```

On Linux-based hosts such as Render, use `export` instead of `set`.

### Password Requirements

When registering, passwords must:

- Be at least 8 characters long
- Contain at least one uppercase letter
- Contain at least one digit

---

## Frontend Dashboard

NutriTrack includes a Vue.js frontend dashboard hosted on GitHub Pages:

https://anhmlpje.github.io/food-nutrition-service/

The frontend automatically connects to the local API when opened locally or from `file://`, and to the hosted Render API when accessed from GitHub Pages. You can override the backend target with `?api=http://your-url`.

| Page | Features |
|------|----------|
| Home | Stats overview, quick search, top protein and nutrient density charts |
| Search | Real-time ingredient search with calorie comparison chart |
| Rankings | Protein, caffeine, and nutrient density leaderboards |
| Compare | Side-by-side ingredient comparison with radar chart |
| Allergens | Allergen exclusion filtering |
| Builder | Login/register, build a recipe, submit via API |
| Analyser | Full nutritional breakdown with charts and health score |

---

## Usage Examples

### Register and login

```bash
curl -X POST https://nutritrack-api-1m8s.onrender.com/users/register \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "Password123"}'

curl -X POST https://nutritrack-api-1m8s.onrender.com/users/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john&password=Password123"
```

### Search ingredients

```bash
curl "https://nutritrack-api-1m8s.onrender.com/ingredients/?search=salmon&limit=5"
curl https://nutritrack-api-1m8s.onrender.com/ingredients/1
```

### Create a recipe

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

### Analyse recipe nutrition

```bash
curl https://nutritrack-api-1m8s.onrender.com/nutrition/recipe/1
```

### Explore analytics

```bash
curl "https://nutritrack-api-1m8s.onrender.com/nutrition/top-protein?limit=10"
curl "https://nutritrack-api-1m8s.onrender.com/nutrition/top-nutrient-density?limit=10"
curl "https://nutritrack-api-1m8s.onrender.com/nutrition/compare?id1=2&id2=3"
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
| GET | `/ingredients/` | List ingredients with search and pagination | No |
| GET | `/ingredients/{id}` | Get ingredient by ID | No |
| PUT | `/ingredients/{id}` | Update ingredient | Yes |
| DELETE | `/ingredients/{id}` | Delete ingredient | Yes |

### Recipes

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/recipes/` | Create recipe with weighted ingredients | Yes |
| GET | `/recipes/` | List recipes with filters and pagination | No |
| GET | `/recipes/{id}` | Get recipe by ID | No |
| PUT | `/recipes/{id}` | Update recipe metadata (owner only) | Yes |
| DELETE | `/recipes/{id}` | Delete recipe (owner only) | Yes |

### Nutrition Analytics

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/nutrition/recipe/{id}` | Full nutrition breakdown, score, warnings, allergens | No |
| GET | `/nutrition/top-protein` | Top ingredients by protein | No |
| GET | `/nutrition/top-caffeine` | Top ingredients by caffeine | No |
| GET | `/nutrition/low-calorie-recipes` | Recipes below a calorie threshold | No |
| GET | `/nutrition/compare` | Side-by-side ingredient comparison | No |
| GET | `/nutrition/top-nutrient-density` | Top ingredients by nutrient density score | No |

### Allergens

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/allergens/ingredient/{id}` | Get allergens for an ingredient | No |
| GET | `/allergens/recipe/{id}` | Get allergen report for a recipe | No |
| GET | `/allergens/free` | Find ingredients free from a specified allergen | No |

---

## API Documentation

Interactive Swagger documentation is available at:

- Local: `http://127.0.0.1:8000/docs`
- Live: `https://nutritrack-api-1m8s.onrender.com/docs`

A PDF export of the API documentation is included in the repository: [api_docs.pdf](./api_docs.pdf)

---

## MCP Server

NutriTrack exposes an MCP server so AI assistants can query nutritional data without manually calling the REST API.

### Available Tools

| Tool | Description |
|------|-------------|
| `search_ingredients` | Search ingredients by name with nutritional data |
| `get_top_protein_ingredients` | Rank ingredients by protein content |
| `get_top_caffeine_ingredients` | Rank ingredients by caffeine content |
| `get_top_nutrient_density` | Rank ingredients by nutrient density score |
| `check_ingredient_allergens` | Detect allergens in a specific ingredient |
| `find_allergen_free_ingredients` | Filter ingredients by allergen exclusion |
| `compare_ingredients` | Compare two ingredients side by side |
| `analyse_recipe_nutrition` | Analyse a custom recipe with quantities |

### Run the MCP server

```bash
python mcp_server.py
```

### Run the MCP smoke test

```bash
python scripts/test_mcp.py
```

### Claude Desktop Integration

Add the `mcpServers` section to your existing Claude Desktop config.

Windows config path:

`C:\Users\<username>\AppData\Local\Packages\Claude_*\LocalCache\Roaming\Claude\claude_desktop_config.json`

Example:

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

---

## Running Tests

```bash
python -m pytest tests/ -v
```

Expected output: **59 passed**

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_allergens.py` | 7 | Allergen queries, recipe allergen reports, allergen-free filtering |
| `test_auth_and_security.py` | 8 | `/users/me`, invalid tokens, failed login, rate limiting, env-based security config |
| `test_ingredients.py` | 17 | CRUD operations, search, pagination, password strength validation |
| `test_mcp_smoke.py` | 3 | MCP tool registration, basic search execution, unknown-tool handling |
| `test_nutrition.py` | 11 | Calorie accuracy, health score range, ranking order, comparison |
| `test_recipes.py` | 10 | CRUD and ownership enforcement |
| `test_seed_db.py` | 3 | Float parsing and compatibility with both `iron` and legacy `irom` CSV headers |

All tests use an isolated SQLite test database. Coverage includes CRUD behaviour, analytics correctness, authentication and rate limiting, seed import compatibility, and MCP smoke validation.

---

## Deployment

### Backend - Render

NutriTrack is deployed on Render with automatic GitHub-based deployment.

- Live URL: `https://nutritrack-api-1m8s.onrender.com`
- Platform: Render
- Start command: `python scripts/seed_db.py && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment variables: `NUTRITRACK_SECRET_KEY`, `APP_ENV`, `NUTRITRACK_TOKEN_EXPIRE_MINUTES`, and optionally `NUTRITRACK_ALLOWED_ORIGINS`

### Frontend - GitHub Pages

- Live URL: `https://anhmlpje.github.io/food-nutrition-service/`
- Platform: GitHub Pages
- Auto-deploy: every push to `main` updates the site

---

## Data Source

Nutritional data comes from:

- Dataset: [Nutritional Values for Common Foods and Products](https://www.kaggle.com/datasets/trolukovich/nutritional-values-for-common-foods-and-products)
- Origin: USDA FoodData Central via Kaggle
- Size: 8,789 items
- Values: expressed per 100g
- License: public domain / suitable for academic use

---

## Novel Features

**Allergen Inference Engine**

Detects 7 allergen categories from ingredient names using keyword matching without requiring a separate allergen dataset.

**Health Score Algorithm**

Computes a 0-100 recipe score based on NHS-style daily reference values, rewarding protein and fibre while penalising excess sodium, sugar, and fat.

**Nutrient Density Score**

Ranks ingredients using a custom formula combining positive nutrients and negative nutrients to identify foods that deliver more value per calorie.

**MCP Integration**

Makes the dataset accessible to AI assistants through Model Context Protocol, not just through REST endpoints.

**Smart Frontend API Detection**

Lets the frontend switch between local and hosted APIs automatically, including support for `file://` use during development.

---

## Generative AI Declaration

This project was developed with the assistance of Claude AI (Anthropic). The technical report documents the tools used, their purposes, and reflective commentary on how GenAI contributed to planning, implementation, debugging, and design exploration.
