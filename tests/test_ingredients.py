import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app import models

# Use a separate in-memory database for testing
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
    """Register and login a test user, return auth headers."""
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
def sample_ingredient(client, auth_headers):
    """Create a sample ingredient and return its data."""
    response = client.post("/ingredients/", json={
        "name": "Test Chicken Breast",
        "calories": 165.0,
        "protein": 31.0,
        "carbohydrate": 0.0,
        "fat": 3.6,
        "fiber": 0.0,
        "sodium": 74.0,
    }, headers=auth_headers)
    return response.json()


class TestCreateIngredient:
    def test_create_ingredient_success(self, client, auth_headers):
        """Authenticated user can create a new ingredient."""
        response = client.post("/ingredients/", json={
            "name": "Brown Rice",
            "calories": 216.0,
            "protein": 5.0,
            "carbohydrate": 45.0,
            "fat": 1.8,
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Brown Rice"
        assert data["calories"] == 216.0
        assert data["id"] is not None

    def test_create_ingredient_unauthenticated(self, client):
        """Unauthenticated request should return 401."""
        response = client.post("/ingredients/", json={
            "name": "Brown Rice",
            "calories": 216.0,
        })
        assert response.status_code == 401

    def test_create_duplicate_ingredient(self, client, auth_headers, sample_ingredient):
        """Creating a duplicate ingredient name should return 400."""
        response = client.post("/ingredients/", json={
            "name": "Test Chicken Breast",
            "calories": 165.0,
        }, headers=auth_headers)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]


class TestGetIngredients:
    def test_get_ingredients_empty(self, client):
        """Returns empty list when no ingredients exist."""
        response = client.get("/ingredients/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_ingredients_with_data(self, client, auth_headers, sample_ingredient):
        """Returns list containing created ingredients."""
        response = client.get("/ingredients/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_ingredients_search(self, client, auth_headers, sample_ingredient):
        """Search filter returns matching ingredients."""
        response = client.get("/ingredients/?search=Chicken")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert "Chicken" in response.json()[0]["name"]

    def test_get_ingredients_search_no_match(self, client, auth_headers, sample_ingredient):
        """Search with no match returns empty list."""
        response = client.get("/ingredients/?search=nonexistent")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_ingredient_by_id(self, client, auth_headers, sample_ingredient):
        """Fetching by valid ID returns correct ingredient."""
        ingredient_id = sample_ingredient["id"]
        response = client.get(f"/ingredients/{ingredient_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Test Chicken Breast"

    def test_get_ingredient_not_found(self, client):
        """Fetching a non-existent ID returns 404."""
        response = client.get("/ingredients/99999")
        assert response.status_code == 404


class TestUpdateIngredient:
    def test_update_ingredient_success(self, client, auth_headers, sample_ingredient):
        """Authenticated user can update an ingredient."""
        ingredient_id = sample_ingredient["id"]
        response = client.put(f"/ingredients/{ingredient_id}", json={
            "calories": 200.0
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["calories"] == 200.0

    def test_update_ingredient_not_found(self, client, auth_headers):
        """Updating a non-existent ingredient returns 404."""
        response = client.put("/ingredients/99999", json={
            "calories": 200.0
        }, headers=auth_headers)
        assert response.status_code == 404


class TestDeleteIngredient:
    def test_delete_ingredient_success(self, client, auth_headers, sample_ingredient):
        """Authenticated user can delete an ingredient."""
        ingredient_id = sample_ingredient["id"]
        response = client.delete(f"/ingredients/{ingredient_id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify it's gone
        response = client.get(f"/ingredients/{ingredient_id}")
        assert response.status_code == 404

    def test_delete_ingredient_unauthenticated(self, client, auth_headers, sample_ingredient):
        """Unauthenticated delete request returns 401."""
        ingredient_id = sample_ingredient["id"]
        response = client.delete(f"/ingredients/{ingredient_id}")
        assert response.status_code == 401