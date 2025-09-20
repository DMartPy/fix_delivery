"""
Схемы для исходящих ответов (response models).
"""

import uuid
from typing import Optional

from pydantic import BaseModel

from .base import TunedModel


class TaskResponse(BaseModel):
    """Схема ответа задачи Celery."""
    task_id: str
    status: str


class PackageGetTypes(TunedModel):
    """Схема типа посылки."""
    id: int
    name: str


class PackageResponse(TunedModel):
    """Схема посылки в ответе."""
    id: uuid.UUID
    name: str
    weight: float
    type_id: int
    price: float
    shipping_cost: Optional[str] = None
    session_id: uuid.UUID


class PaginatedPackagesResponse(BaseModel):
    """Схема пагинированного ответа с посылками."""
    packages: list[PackageResponse]
    total: int
    page: int
    size: int
    pages: int


class SessionResponse(TunedModel):
    """Схема сессии."""
    id: uuid.UUID
    created_at: str
    last_activity: str


class PackageInfo(TunedModel):
    """Схема детальной информации о посылке."""
    id: uuid.UUID
    name: str
    weight: float
    type_id: int
    price: float
    shipping_cost: Optional[str] = None


class GetPackageID(TunedModel):
    """Схема для получения ID посылки."""
    id: uuid.UUID
