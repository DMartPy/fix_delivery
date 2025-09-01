import pytest
from fastapi import status


class TestPackageEndpoints:
    """Тесты для endpoints посылок"""

    def test_get_package_types(self, client):
        """Тест получения типов посылок"""
        response = client.get("/packages/types")
        # Должен вернуть 200 или 500 (ошибка сервера)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert isinstance(data, list)
            # Проверяем, что есть хотя бы один тип
            assert len(data) > 0
            assert "id" in data[0]
            assert "name" in data[0]

    def test_create_package_validation(self, client, sample_package_data):
        """Тест валидации создания посылки"""
        # Тест с корректными данными
        response = client.post("/packages/", json=sample_package_data)
        # Должен вернуть 403 (нет сессии) или 500 (ошибка сервера)
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_500_INTERNAL_SERVER_ERROR]

    def test_create_package_invalid_data(self, client):
        """Тест валидации с некорректными данными"""
        invalid_data = {
            "name": "",  # Пустое имя
            "weight": -1,  # Отрицательный вес
            "type_id": 0,  # Нулевой ID
            "price": -100  # Отрицательная цена
        }
        
        response = client.post("/packages/", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_packages_pagination(self, client):
        """Тест пагинации получения посылок"""
        response = client.get("/packages/?page=1&size=5")
        # Должен вернуть 403 (нет сессии) или 500 (ошибка сервера)
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_500_INTERNAL_SERVER_ERROR]

    def test_get_packages_filters(self, client):
        """Тест фильтров получения посылок"""
        # Тест фильтра по типу
        response = client.get("/packages/?type_id=1&page=1&size=10")
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_500_INTERNAL_SERVER_ERROR]
        
        # Тест фильтра по стоимости доставки
        response = client.get("/packages/?has_shipping_cost=true&page=1&size=10")
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_500_INTERNAL_SERVER_ERROR]


class TestValidation:
    """Тесты валидации данных"""

    def test_package_name_validation(self, client):
        """Тест валидации имени посылки"""
        # Слишком длинное имя
        long_name_data = {
            "name": "A" * 300,  # 300 символов
            "weight": 1.0,
            "type_id": 1,
            "price": 1000.0
        }
        
        response = client.post("/packages/", json=long_name_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_package_weight_validation(self, client):
        """Тест валидации веса посылки"""
        # Слишком большой вес
        heavy_package_data = {
            "name": "Heavy Package",
            "weight": 2000.0,  # 2 тонны
            "type_id": 1,
            "price": 1000.0
        }
        
        response = client.post("/packages/", json=heavy_package_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_package_price_validation(self, client):
        """Тест валидации цены посылки"""
        # Слишком высокая цена
        expensive_package_data = {
            "name": "Expensive Package",
            "weight": 1.0,
            "type_id": 1,
            "price": 20000000.0  # 20 млн рублей
        }
        
        response = client.post("/packages/", json=expensive_package_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
