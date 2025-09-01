import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from dostavka.main import app


@pytest.fixture
def client():
    """Синхронный тестовый клиент"""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Асинхронный тестовый клиент"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_package_data():
    """Тестовые данные для посылки"""
    return {
        "name": "Test Package",
        "weight": 1.5,
        "type_id": 1,
        "price": 1000.0
    }
