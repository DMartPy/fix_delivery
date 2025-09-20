"""
Сервис для работы с посылками.

Содержит бизнес-логику, валидацию и обработку данных.
"""

from typing import Optional

from src.repositories.packages import PackageRepository
from src.repositories.sessions import SessionRepository
from src.schemas.requests import PackageCreate
from src.schemas.responses import PackageInfo, TaskResponse
from src.services.sessions import check_session
from src.utils.celery.tasks import calculate_and_save
from src.utils.logging import get_logger

logger = get_logger(__name__)


class PackageService:
    """Сервис для работы с посылками."""
    
    def __init__(self, package_repository: PackageRepository, session_repository: SessionRepository):
        self.package_repository = package_repository
        self.session_repository = session_repository
    
    async def create_package(self, package_data: PackageCreate, session_id: str) -> TaskResponse:
        """Создать новую посылку."""
        # Проверяем/создаем сессию
        session = await check_session(session_id, self.package_repository, self.session_repository)
        
        # Создаем посылку
        package_dict = package_data.model_dump()
        package_dict["session_id"] = session.id
        
        package = await self.package_repository.create(package_dict)
        
        # Отправляем задачу в Celery для расчета стоимости
        task = calculate_and_save.delay(str(package.id))
        
        logger.info(f"Создана посылка {package.id}, задача {task.id} отправлена в Celery")
        
        return TaskResponse(task_id=task.id, status="processing")
    
    async def get_packages(
        self, 
        session_id: str, 
        page: int = 1, 
        size: int = 10,
        type_id: Optional[int] = None,
        has_shipping_cost: Optional[bool] = None
    ) -> tuple[list[PackageInfo], int, int, int]:
        """Получить посылки с пагинацией и фильтрацией."""
        packages, total = await self.package_repository.get_by_session_id(
            session_id, page, size, type_id, has_shipping_cost
        )
        
        package_infos = [
            PackageInfo(
                id=pkg.id,
                name=pkg.name,
                weight=pkg.weight,
                type_id=pkg.type_id,
                price=pkg.price,
                shipping_cost=pkg.shipping_cost
            )
            for pkg in packages
        ]
        
        pages = (total + size - 1) // size
        
        return package_infos, total, page, pages
    
    async def get_package_by_id(self, package_id: str, session_id: str) -> Optional[PackageInfo]:
        """Получить посылку по ID."""
        package = await self.package_repository.get_by_id(package_id)
        
        if not package or str(package.session_id) != session_id:
            return None
        
        return PackageInfo(
            id=package.id,
            name=package.name,
            weight=package.weight,
            type_id=package.type_id,
            price=package.price,
            shipping_cost=package.shipping_cost
        )
    
    async def get_package_types(self) -> list:
        """Получить все типы посылок."""
        types = await self.package_repository.get_all_types()
        return [{"id": t.id, "name": t.name} for t in types]
