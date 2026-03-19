import pytest
from unittest.mock import patch
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
        "password": "Password123"
    })
    response = client.post("/users/login", data={
        "username": "testuser",
        "password": "Password123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestIngredientAllergens:
    def test_get_allergens_for_nut_ingredient(self, client, auth_headers):
        """Nut ingredient correctly returns nuts allergen."""
        ing = client.post("/ingredients/", json={
            "name": "Almonds, raw",
            "calories": 579.0,
            "allergens": "nuts"
        }, headers=auth_headers).json()

        response = client.get(f"/allergens/ingredient/{ing['id']}")
        assert response.status_code == 200
        data = response.json()
        assert "nuts" in data["allergens"]
        assert data["allergen_free"] is False

    def test_get_allergens_for_safe_ingredient(self, client, auth_headers):
        """Allergen-free ingredient returns empty allergen list."""
        ing = client.post("/ingredients/", json={
            "name": "Broccoli, raw",
            "calories": 34.0,
            "allergens": ""
        }, headers=auth_headers).json()

        response = client.get(f"/allergens/ingredient/{ing['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["allergens"] == []
        assert data["allergen_free"] is True

    def test_get_allergens_ingredient_not_found(self, client):
        """Non-existent ingredient returns 404."""
        response = client.get("/allergens/ingredient/99999")
        assert response.status_code == 404


class TestRecipeAllergens:
    def test_get_recipe_allergen_report(self, client, auth_headers):
        """Recipe allergen report aggregates allergens from all ingredients."""
        ing1 = client.post("/ingredients/", json={
            "name": "Wheat flour",
            "calories": 364.0,
            "allergens": "gluten"
        }, headers=auth_headers).json()

        ing2 = client.post("/ingredients/", json={
            "name": "Butter",
            "calories": 717.0,
            "allergens": "dairy"
        }, headers=auth_headers).json()

        recipe = client.post("/recipes/", json={
            "name": "Shortbread",
            "ingredients": [
                {"ingredient_id": ing1["id"], "quantity_g": 200},
                {"ingredient_id": ing2["id"], "quantity_g": 100},
            ]
        }, headers=auth_headers).json()

        response = client.get(f"/allergens/recipe/{recipe['id']}")
        assert response.status_code == 200
        data = response.json()
        assert "gluten" in data["allergen_report"]
        assert "dairy" in data["allergen_report"]
        assert data["total_allergens_detected"] == 2
        assert data["safe_for_allergies"] is False

    def test_get_recipe_allergens_not_found(self, client):
        """Non-existent recipe returns 404."""
        response = client.get("/allergens/recipe/99999")
        assert response.status_code == 404


class TestAllergenFreeSearch:
    def test_find_gluten_free_ingredients(self, client, auth_headers):
        """Returns ingredients not containing gluten."""
        client.post("/ingredients/", json={
            "name": "Rice, white",
            "calories": 130.0,
            "allergens": ""
        }, headers=auth_headers)

        response = client.get("/allergens/free?exclude=gluten&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["allergen_excluded"] == "gluten"
        assert data["count"] >= 1

    def test_unsupported_allergen_returns_400(self, client):
        """Unsupported allergen type returns 400."""
        response = client.get("/allergens/free?exclude=uranium")
        assert response.status_code == 400