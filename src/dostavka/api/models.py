import uuid
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class TunedModel(BaseModel):
    class Config:
        from_attributes = True  # Исправляем orm_mode на from_attributes


class GetPackageID(TunedModel):
    id: uuid.UUID


class TaskResponse(BaseModel):
    task_id: str
    status: str


class PackageGetTypes(TunedModel):
    id: int
    name: str


class PackageCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    weight: float = Field(..., gt=0)
    type_id: int = Field(..., gt=0)
    price: float = Field(..., gt=0)

    @field_validator('name')
    @classmethod
    def validate_name(cls, value):
        if not value or not value.strip():
            raise ValueError('Название посылки не может быть пустым')
        if len(value.strip()) < 1:
            raise ValueError('Название посылки должно содержать минимум 1 символ')
        if len(value.strip()) > 255:
            raise ValueError('Название посылки не может превышать 255 символов')
        return value.strip()


    @field_validator('weight')
    @classmethod
    def validate_weight(cls, value):
        if value <= 0:
            raise ValueError('Вес посылки должен быть больше 0')
        if value > 1000:  # Максимальный вес 1 тонна
            raise ValueError('Вес посылки не может превышать 1000 кг')
        return value


    @field_validator('price')
    @classmethod
    def validate_price(cls, value):
        if value <= 0:
            raise ValueError('Стоимость товара должна быть больше 0')
        if value > 10000000:  # Максимальная стоимость 10 млн рублей
            raise ValueError('Стоимость товара не может превышать 10 000 000 рублей')
        return value


    @field_validator('type_id')
    @classmethod
    def validate_type_id(cls, value):
        if value <= 0:
            raise ValueError('ID типа посылки должен быть положительным числом')
        return value


class PackageResponse(TunedModel):
    id: uuid.UUID
    name: str
    weight: float
    type_id: int
    price: float
    shipping_cost: Optional[float] = None
    session_id: uuid.UUID


class PaginatedPackagesResponse(BaseModel):
    packages: List[PackageResponse]
    total: int
    page: int
    size: int
    pages: int


class SessionResponse(TunedModel):
    id: uuid.UUID
    created_at: str
    last_activity: str


class PackageInfo(TunedModel):
    id: uuid.UUID
    name: str
    weight: float
    type_id: int
    price: float
    shipping_cost: Optional[float] = None






