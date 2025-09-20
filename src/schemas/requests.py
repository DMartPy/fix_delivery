"""
Схемы для входящих запросов (request models).
"""

from pydantic import BaseModel, Field


class PackageCreate(BaseModel):
    """Схема для создания посылки."""
    name: str = Field(..., description="Название посылки", min_length=1, max_length=255)
    weight: float = Field(..., description="Вес посылки в кг", gt=0)
    type_id: int = Field(..., description="ID типа посылки", gt=0)
    price: float = Field(..., description="Цена посылки в рублях", ge=0)
