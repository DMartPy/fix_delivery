import pytest
from pydantic import ValidationError

from src.models.db import PackageCreate, TaskResponse, PackageGetTypes


class TestPackageCreate:
    """Тесты для модели создания посылки"""

    def test_valid_package_data(self):
        """Тест валидных данных"""
        data = {
            "name": "Test Package",
            "weight": 1.5,
            "type_id": 1,
            "price": 1000.0
        }
        
        package = PackageCreate(**data)
        assert package.name == "Test Package"
        assert package.weight == 1.5
        assert package.type_id == 1
        assert package.price == 1000.0

    def test_invalid_name_empty(self):
        """Тест пустого имени"""
        data = {
            "name": "",
            "weight": 1.5,
            "type_id": 1,
            "price": 1000.0
        }
        
        with pytest.raises(ValidationError):
            PackageCreate(**data)

    def test_invalid_name_too_long(self):
        """Тест слишком длинного имени"""
        data = {
            "name": "A" * 300,  # 300 символов
            "weight": 1.5,
            "type_id": 1,
            "price": 1000.0
        }
        
        with pytest.raises(ValidationError):
            PackageCreate(**data)

    def test_invalid_weight_negative(self):
        """Тест отрицательного веса"""
        data = {
            "name": "Test Package",
            "weight": -1.0,
            "type_id": 1,
            "price": 1000.0
        }
        
        with pytest.raises(ValidationError):
            PackageCreate(**data)

    def test_invalid_weight_zero(self):
        """Тест нулевого веса"""
        data = {
            "name": "Test Package",
            "weight": 0.0,
            "type_id": 1,
            "price": 1000.0
        }
        
        with pytest.raises(ValidationError):
            PackageCreate(**data)

    def test_invalid_price_negative(self):
        """Тест отрицательной цены"""
        data = {
            "name": "Test Package",
            "weight": 1.5,
            "type_id": 1,
            "price": -100.0
        }
        
        with pytest.raises(ValidationError):
            PackageCreate(**data)

    def test_invalid_type_id_zero(self):
        """Тест нулевого ID типа"""
        data = {
            "name": "Test Package",
            "weight": 1.5,
            "type_id": 0,
            "price": 1000.0
        }
        
        with pytest.raises(ValidationError):
            PackageCreate(**data)

    def test_name_stripping(self):
        """Тест автоматического удаления пробелов в имени"""
        data = {
            "name": "  Test Package  ",
            "weight": 1.5,
            "type_id": 1,
            "price": 1000.0
        }
        
        package = PackageCreate(**data)
        assert package.name == "Test Package"


class TestTaskResponse:
    """Тесты для модели ответа задачи"""

    def test_valid_task_response(self):
        """Тест валидного ответа задачи"""
        data = {
            "task_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "processing"
        }
        
        response = TaskResponse(**data)
        assert response.task_id == "550e8400-e29b-41d4-a716-446655440000"
        assert response.status == "processing"


class TestPackageGetTypes:
    """Тесты для модели типа посылки"""

    def test_valid_package_type(self):
        """Тест валидного типа посылки"""
        data = {
            "id": 1,
            "name": "Электроника"
        }
        
        package_type = PackageGetTypes(**data)
        assert package_type.id == 1
        assert package_type.name == "Электроника"
