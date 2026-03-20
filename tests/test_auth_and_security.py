import importlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_allowed_origins
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
        "username": "secureuser",
        "email": "secure@example.com",
        "password": "Password123"
    })
    response = client.post("/users/login", data={
        "username": "secureuser",
        "password": "Password123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestCurrentUserEndpoint:
    def test_get_me_success(self, client, auth_headers):
        response = client.get("/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "secureuser"
        assert data["email"] == "secure@example.com"

    def test_get_me_without_token_returns_401(self, client):
        response = client.get("/users/me")
        assert response.status_code == 401

    def test_get_me_with_invalid_token_returns_401(self, client):
        response = client.get(
            "/users/me",
            headers={"Authorization": "Bearer definitely-invalid-token"}
        )
        assert response.status_code == 401


class TestAuthenticationFailures:
    def test_login_with_wrong_password_returns_401(self, client):
        client.post("/users/register", json={
            "username": "wrongpass",
            "email": "wrongpass@example.com",
            "password": "Password123"
        })
        response = client.post("/users/login", data={
            "username": "wrongpass",
            "password": "WrongPassword123"
        })
        assert response.status_code == 401


class TestRateLimiting:
    def test_register_rate_limit_enforced(self, client):
        for i in range(5):
            response = client.post("/users/register", json={
                "username": f"user{i}",
                "email": f"user{i}@example.com",
                "password": "Password123"
            })
            assert response.status_code == 201

        response = client.post("/users/register", json={
            "username": "user-final",
            "email": "user-final@example.com",
            "password": "Password123"
        })
        assert response.status_code == 429


class TestSecurityConfiguration:
    def test_default_allowed_origins_include_local_and_deployed_clients(self, monkeypatch):
        monkeypatch.delenv("NUTRITRACK_ALLOWED_ORIGINS", raising=False)
        origins = get_allowed_origins()
        assert "http://127.0.0.1:8000" in origins
        assert "https://anhmlpje.github.io" in origins

    def test_allowed_origins_can_be_overridden_by_env(self, monkeypatch):
        monkeypatch.setenv(
            "NUTRITRACK_ALLOWED_ORIGINS",
            "https://example.com, https://frontend.example.com"
        )
        origins = get_allowed_origins()
        assert origins == ["https://example.com", "https://frontend.example.com"]

    def test_production_requires_non_default_secret_key(self, monkeypatch):
        monkeypatch.setenv("APP_ENV", "production")
        monkeypatch.delenv("NUTRITRACK_SECRET_KEY", raising=False)

        import app.auth as auth_module
        auth_module = importlib.reload(auth_module)

        with pytest.raises(RuntimeError):
            auth_module.ensure_auth_config()

        monkeypatch.setenv("NUTRITRACK_SECRET_KEY", "super-secret-for-tests")
        auth_module = importlib.reload(auth_module)
        auth_module.ensure_auth_config()
