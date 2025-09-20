"""
Роуты для работы с посылками.
"""

import math
from typing import Optional

from fastapi import APIRouter, HTTPException

from src.repositories.packages import PackageRepository
from src.repositories.sessions import SessionRepository
from src.schemas.requests import PackageCreate
from src.services.packages import PackageService
from src.utils.logging import get_logger

logger = get_logger(__name__)

package_router = APIRouter()


async def _create_new_package(package_data: PackageCreate, session_id: str, db):
    """Создать новую посылку."""
    package_repository = PackageRepository(db)
    session_repository = SessionRepository(db)
    package_service = PackageService(package_repository, session_repository)
    
    return await package_service.create_package(package_data, session_id)


async def _get_user_packages(session_id: str, db, page: int, size: int, type_id: Optional[int], has_shipping_cost: Optional[bool]):
    """Получить посылки пользователя с пагинацией."""
    package_repository = PackageRepository(db)
    session_repository = SessionRepository(db)
    package_service = PackageService(package_repository, session_repository)
    
    packages, total, current_page, pages = await package_service.get_packages(
        session_id, page, size, type_id, has_shipping_cost
    )
    
    from src.schemas.responses import PaginatedPackagesResponse, PackageResponse
    
    package_responses = [
        PackageResponse(
            id=pkg.id,
            name=pkg.name,
            weight=pkg.weight,
            type_id=pkg.type_id,
            price=pkg.price,
            shipping_cost=pkg.shipping_cost,
            session_id=session_id
        )
        for pkg in packages
    ]
    
    return PaginatedPackagesResponse(
        packages=package_responses,
        total=total,
        page=current_page,
        size=size,
        pages=pages
    )


async def _get_all_packages_types(db):
    """Получить все типы посылок."""
    package_repository = PackageRepository(db)
    session_repository = SessionRepository(db)
    package_service = PackageService(package_repository, session_repository)
    
    return await package_service.get_package_types()


async def _get_package_info(package_id: str, session_id: str, db):
    """Получить информацию о посылке."""
    package_repository = PackageRepository(db)
    session_repository = SessionRepository(db)
    package_service = PackageService(package_repository, session_repository)
    
    package = await package_service.get_package_by_id(package_id, session_id)
    
    if not package:
        raise HTTPException(status_code=404, detail="Посылка не найдена")
    
    return package
