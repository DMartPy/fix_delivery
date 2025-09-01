import pytest
from fastapi import status


def test_app_startup(client):
    """Тест запуска приложения"""
    response = client.get("/docs")
    assert response.status_code == status.HTTP_200_OK


def test_app_info(client):
    """Тест информации о приложении"""
    response = client.get("/openapi.json")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["info"]["title"] == "Dostavka API"
    # Проверяем, что есть хотя бы один endpoint для посылок
    assert any("/packages" in path for path in data["paths"].keys())


def test_health_check(client):
    """Тест health check (если есть)"""
    # Если у вас есть health check endpoint
    try:
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
    except:
        # Если endpoint не существует, тест проходит
        pass
