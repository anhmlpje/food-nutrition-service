import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    client.post("/users/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    })
    response = client.post("/users/login", data={
        "username": "testuser",
        "password": "password123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def recipe_with_ingredients(client, auth_headers):
    """Create a recipe with two ingredients for nutrition testing."""
    ing1 = client.post("/ingredients/", json={
        "name": "Oats",
        "calories": 389.0,
        "protein": 17.0,
        "carbohydrate": 66.0,
        "fat": 7.0,
        "fiber": 10.6,
        "sodium": 2.0,
        "allergens": "gluten"
    }, headers=auth_headers).json()

    ing2 = client.post("/ingredients/", json={
        "name": "Whole Milk",
        "calories": 61.0,
        "protein": 3.2,
        "carbohydrate": 4.8,
        "fat": 3.3,
        "sodium": 44.0,
        "allergens": "dairy"
    }, headers=auth_headers).json()

    recipe = client.post("/recipes/", json={
        "name": "Oatmeal",
        "cuisine_type": "British",
        "difficulty": "easy",
        "prep_time_minutes": 10,
        "ingredients": [
            {"ingredient_id": ing1["id"], "quantity_g": 80},
            {"ingredient_id": ing2["id"], "quantity_g": 200},
        ]
    }, headers=auth_headers).json()

    return recipe


class TestRecipeNutrition:
    def test_get_recipe_nutrition(self, client, recipe_with_ingredients):
        """Nutrition endpoint returns correct calculated totals."""
        recipe_id = recipe_with_ingredients["id"]
        response = client.get(f"/nutrition/recipe/{recipe_id}")
        assert response.status_code == 200
        data = response.json()

        assert "nutrition" in data
        assert "health_score" in data
        assert "warnings" in data
        assert "allergens" in data

        # 80g oats + 200g milk — verify calorie calculation
        expected_calories = round(389 * 0.8 + 61 * 2.0, 1)
        assert abs(data["nutrition"]["calories"] - expected_calories) < 1.0

    def test_recipe_allergens_detected(self, client, recipe_with_ingredients):
        """Allergens from all ingredients are correctly aggregated."""
        recipe_id = recipe_with_ingredients["id"]
        response = client.get(f"/nutrition/recipe/{recipe_id}")
        allergens = response.json()["allergens"]
        assert "gluten" in allergens
        assert "dairy" in allergens

    def test_nutrition_recipe_not_found(self, client):
        """Non-existent recipe returns 404."""
        response = client.get("/nutrition/recipe/99999")
        assert response.status_code == 404

    def test_health_score_range(self, client, recipe_with_ingredients):
        """Health score is always between 0 and 100."""
        recipe_id = recipe_with_ingredients["id"]
        response = client.get(f"/nutrition/recipe/{recipe_id}")
        score = response.json()["health_score"]
        assert 0 <= score <= 100


class TestTopProtein:
    def test_top_protein_returns_list(self, client, auth_headers):
        """Top protein endpoint returns a ranked list."""
        client.post("/ingredients/", json={
            "name": "Protein Powder",
            "calories": 120.0,
            "protein": 25.0,
        }, headers=auth_headers)
        response = client.get("/nutrition/top-protein?limit=5")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_top_protein_ordering(self, client, auth_headers):
        """Results are ordered by protein descending."""
        client.post("/ingredients/", json={
            "name": "Low Protein Food",
            "calories": 100.0,
            "protein": 2.0,
        }, headers=auth_headers)
        client.post("/ingredients/", json={
            "name": "High Protein Food",
            "calories": 200.0,
            "protein": 40.0,
        }, headers=auth_headers)

        response = client.get("/nutrition/top-protein?limit=2")
        results = response.json()
        assert results[0]["protein_per_100g"] >= results[1]["protein_per_100g"]


class TestCompareIngredients:
    def test_compare_two_ingredients(self, client, auth_headers):
        """Comparison endpoint returns side-by-side nutritional data."""
        ing1 = client.post("/ingredients/", json={
            "name": "Apple",
            "calories": 52.0,
            "protein": 0.3,
            "carbohydrate": 14.0,
        }, headers=auth_headers).json()

        ing2 = client.post("/ingredients/", json={
            "name": "Banana",
            "calories": 89.0,
            "protein": 1.1,
            "carbohydrate": 23.0,
        }, headers=auth_headers).json()

        response = client.get(f"/nutrition/compare?id1={ing1['id']}&id2={ing2['id']}")
        assert response.status_code == 200
        data = response.json()
        assert "comparison_per_100g" in data
        assert "calories" in data["comparison_per_100g"]

    def test_compare_invalid_ingredient(self, client, auth_headers):
        """Comparing with a non-existent ingredient returns 404."""
        ing = client.post("/ingredients/", json={
            "name": "Apple",
            "calories": 52.0,
        }, headers=auth_headers).json()

        response = client.get(f"/nutrition/compare?id1={ing['id']}&id2=99999")
        assert response.status_code == 404