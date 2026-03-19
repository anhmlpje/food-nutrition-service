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
    """Create tables before each test and drop after."""
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

@pytest.fixture
def sample_ingredient(client, auth_headers):
    response = client.post("/ingredients/", json={
        "name": "Chicken Breast",
        "calories": 165.0,
        "protein": 31.0,
        "carbohydrate": 0.0,
        "fat": 3.6,
    }, headers=auth_headers)
    return response.json()

@pytest.fixture
def sample_recipe(client, auth_headers, sample_ingredient):
    response = client.post("/recipes/", json={
        "name": "Grilled Chicken",
        "description": "Simple grilled chicken breast",
        "cuisine_type": "American",
        "difficulty": "easy",
        "prep_time_minutes": 20,
        "ingredients": [
            {"ingredient_id": sample_ingredient["id"], "quantity_g": 200}
        ]
    }, headers=auth_headers)
    return response.json()


class TestCreateRecipe:
    def test_create_recipe_success(self, client, auth_headers, sample_ingredient):
        """Authenticated user can create a recipe with ingredients."""
        response = client.post("/recipes/", json={
            "name": "Grilled Chicken",
            "description": "Simple grilled chicken",
            "cuisine_type": "American",
            "difficulty": "easy",
            "prep_time_minutes": 20,
            "ingredients": [
                {"ingredient_id": sample_ingredient["id"], "quantity_g": 200}
            ]
        }, headers=auth_headers)
        assert response.status_code == 201
        assert response.json()["name"] == "Grilled Chicken"

    def test_create_recipe_invalid_ingredient(self, client, auth_headers):
        """Creating a recipe with a non-existent ingredient returns 404."""
        response = client.post("/recipes/", json={
            "name": "Invalid Recipe",
            "ingredients": [{"ingredient_id": 99999, "quantity_g": 100}]
        }, headers=auth_headers)
        assert response.status_code == 404

    def test_create_recipe_unauthenticated(self, client):
        """Unauthenticated recipe creation returns 401."""
        response = client.post("/recipes/", json={"name": "Test"})
        assert response.status_code == 401


class TestGetRecipes:
    def test_get_recipes_empty(self, client):
        """Returns empty list when no recipes exist."""
        response = client.get("/recipes/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_recipe_by_id(self, client, sample_recipe):
        """Fetching by valid ID returns correct recipe."""
        recipe_id = sample_recipe["id"]
        response = client.get(f"/recipes/{recipe_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Grilled Chicken"

    def test_get_recipe_not_found(self, client):
        """Fetching a non-existent recipe returns 404."""
        response = client.get("/recipes/99999")
        assert response.status_code == 404

    def test_filter_by_difficulty(self, client, auth_headers, sample_recipe):
        """Filtering by difficulty returns matching recipes."""
        response = client.get("/recipes/?difficulty=easy")
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestUpdateRecipe:
    def test_update_recipe_success(self, client, auth_headers, sample_recipe):
        """Owner can update their recipe."""
        recipe_id = sample_recipe["id"]
        response = client.put(f"/recipes/{recipe_id}", json={
            "name": "Updated Chicken"
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Chicken"

    def test_update_recipe_not_owner(self, client, sample_recipe):
        """Non-owner cannot update a recipe — returns 403."""
        recipe_id = sample_recipe["id"]
        # Register a second user
        client.post("/users/register", json={
            "username": "otheruser",
            "email": "other@example.com",
            "password": "Password123"
        })
        login = client.post("/users/login", data={
            "username": "otheruser",
            "password": "Password123"
        })
        other_token = login.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}

        response = client.put(f"/recipes/{recipe_id}", json={
            "name": "Hacked Recipe"
        }, headers=other_headers)
        assert response.status_code == 403


class TestDeleteRecipe:
    def test_delete_recipe_success(self, client, auth_headers, sample_recipe):
        """Owner can delete their recipe."""
        recipe_id = sample_recipe["id"]
        response = client.delete(f"/recipes/{recipe_id}", headers=auth_headers)
        assert response.status_code == 204

        response = client.get(f"/recipes/{recipe_id}")
        assert response.status_code == 404