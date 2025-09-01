from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import func, select

from dostavka.db.models import Package, PackageType, Session
from dostavka.db.session import AsyncSession


class SessionDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_session(self, session_id: str) -> Session:
        """Создать новую сессию с указанным ID"""
        session = Session(id=session_id)
        self.db_session.add(session)
        await self.db_session.flush()
        return session

    async def get_session_by_id(self, session_id: str) -> Session:
        """Получить сессию по ID"""
        query = select(Session).where(Session.id == session_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def update_last_activity(self, session_id: str):
        """Обновить время последней активности"""
        query = select(Session).where(Session.id == session_id)
        result = await self.db_session.execute(query)
        session = result.scalar_one_or_none()

        if session:
            session.last_activity = datetime.utcnow()
            await self.db_session.flush()


class PackageDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_package(self, name: str, weight: float, type_id: int, price: float, session_id: str, shipping_cost: float = None) -> Package:
        package = Package(
            name=name,
            weight=weight,
            type_id=type_id,
            price=price,
            shipping_cost=shipping_cost,
            session_id=session_id
        )

        self.db_session.add(package)
        await self.db_session.flush()
        return package

    async def get_packages_by_session(self, session_id: str):
        """Получить посылки конкретной сессии"""
        query = select(Package).where(Package.session_id == session_id)
        result = await self.db_session.execute(query)
        packages = result.scalars().all()
        return packages

    async def get_packages_by_session_with_filters(
        self,
        session_id: str,
        page: int = 1,
        size: int = 10,
        type_id: Optional[int] = None,
        has_shipping_cost: Optional[bool] = None
    ) -> Tuple[List[Package], int]:
        """Получить посылки с фильтрацией и пагинацией"""
        # Базовый запрос
        query = select(Package).where(Package.session_id == session_id)

        # Применяем фильтры
        if type_id is not None:
            query = query.where(Package.type_id == type_id)

        if has_shipping_cost is not None:
            if has_shipping_cost:
                # Показываем только те, где есть числовое значение (не "Не рассчитано")
                query = query.where(
                    (Package.shipping_cost != "Не рассчитано") &
                    (Package.shipping_cost.isnot(None))
                )
            else:
                # Показываем только те, где "Не рассчитано" или NULL
                query = query.where(
                    (Package.shipping_cost == "Не рассчитано") |
                    (Package.shipping_cost.is_(None))
                )

        # Подсчитываем общее количество
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db_session.execute(count_query)
        total = count_result.scalar()

        # Применяем пагинацию
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        # Выполняем запрос
        result = await self.db_session.execute(query)
        packages = result.scalars().all()

        return packages, total

    async def get_package_by_id_and_session(self, package_id: str, session_id: str) -> Package:
        """Получить посылку по ID, принадлежащую конкретной сессии"""
        query = select(Package).where(
            Package.id == package_id,
            Package.session_id == session_id
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def update_shipping_cost(self, package_id: str, shipping_cost: float, session_id: str) -> Package:
        """Обновить стоимость доставки для посылки конкретной сессии"""
        package = await self.get_package_by_id_and_session(package_id, session_id)

        if package:
            package.shipping_cost = shipping_cost
            await self.db_session.flush()

        return package

    async def get_all_packages(self):
        query = select(Package)
        result = await self.db_session.execute(query)
        packages = result.scalars().all()
        return packages

    async def get_packeges_all_type(self):
        query = select(PackageType)
        res = await self.db_session.execute(query)
        package_types = res.scalars().all()

        return package_types
