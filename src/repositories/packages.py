"""
Репозиторий для работы с посылками в базе данных.
"""

import uuid
from typing import Optional

from sqlalchemy import func, select

from src.db.session import AsyncSession
from src.models.db import Package, PackageType


class PackageRepository:
    """
    Репозиторий для работы с посылками в базе данных.
    
    Содержит методы для CRUD операций с посылками.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, package_data: dict) -> Package:
        """Создать новую посылку."""
        package = Package(**package_data)
        self.session.add(package)
        await self.session.commit()
        await self.session.refresh(package)
        return package
    
    async def get_by_id(self, package_id: str) -> Optional[Package]:
        """Получить посылку по ID."""
        result = await self.session.execute(
            select(Package).where(Package.id == uuid.UUID(package_id))
        )
        return result.scalar_one_or_none()
    
    async def get_by_session_id(
        self, 
        session_id: str, 
        page: int = 1, 
        size: int = 10,
        type_id: Optional[int] = None,
        has_shipping_cost: Optional[bool] = None
    ) -> tuple[list[Package], int]:
        """Получить посылки по session_id с пагинацией и фильтрацией."""
        query = select(Package).where(Package.session_id == uuid.UUID(session_id))
        
        # Применяем фильтры
        if type_id is not None:
            query = query.where(Package.type_id == type_id)
        
        if has_shipping_cost is not None:
            if has_shipping_cost:
                query = query.where(Package.shipping_cost != "Не рассчитано")
            else:
                query = query.where(Package.shipping_cost == "Не рассчитано")
        
        # Подсчитываем общее количество
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()
        
        # Применяем пагинацию
        offset = (page - 1) * size
        query = query.offset(offset).limit(size).order_by(Package.id.desc())
        
        result = await self.session.execute(query)
        packages = result.scalars().all()
        
        return list(packages), total
    
    async def get_all_types(self) -> list[PackageType]:
        """Получить все типы посылок."""
        result = await self.session.execute(select(PackageType))
        return list(result.scalars().all())
    
    async def update_shipping_cost(self, package_id: str, shipping_cost: str) -> Optional[Package]:
        """Обновить стоимость доставки посылки."""
        package = await self.get_by_id(package_id)
        if package:
            package.shipping_cost = shipping_cost
            await self.session.commit()
            await self.session.refresh(package)
        return package
