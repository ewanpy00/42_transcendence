import os

# Must be set before `app` is imported: settings are read at import time.
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-long-enough-0123456789")

import fakeredis  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.deps import get_redis, get_user_repository  # noqa: E402
from app.main import app  # noqa: E402
from app.services.auth import InMemoryUserRepository  # noqa: E402


@pytest.fixture
def redis():
    return fakeredis.FakeAsyncRedis(decode_responses=True)


@pytest.fixture
def client(redis):
    users = InMemoryUserRepository()
    app.dependency_overrides[get_redis] = lambda: redis
    app.dependency_overrides[get_user_repository] = lambda: users
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
