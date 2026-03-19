import pytest
from app.main import app
from app.limiter import limiter

@pytest.fixture(autouse=True)
def reset_rate_limit():
    """Reset rate limit storage before each test to prevent counter carry-over."""
    try:
        limiter._storage.reset()
    except Exception:
        pass
    app.state.limiter = limiter
    yield
    try:
        limiter._storage.reset()
    except Exception:
        pass