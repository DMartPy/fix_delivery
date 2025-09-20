from typing import Optional

from fastapi import APIRouter, Depends, Query, Request

from src.db.session import AsyncSession, get_db
from src.routes.packages import (
    _create_new_package,
    _get_all_packages_types,
    _get_package_info,
    _get_user_packages,
)
from src.schemas.requests import PackageCreate
from src.schemas.responses import (
    PackageGetTypes,
    PackageInfo,
    PaginatedPackagesResponse,
    TaskResponse,
)

package_router = APIRouter()


@package_router.post("/", response_model=TaskResponse, tags=["Посылки"])
async def create_package(body: PackageCreate, request: Request, db: AsyncSession = Depends(get_db)) -> TaskResponse:
    """
    Создать новую посылку для текущей сессии.

    Отправляет задачу в Celery для расчета стоимости доставки.
    Подробная документация доступна в README.md.
    """
    session_id = request.state.session_id
    return await _create_new_package(body, session_id, db)


@package_router.get("/", response_model=PaginatedPackagesResponse, tags=["Посылки"])
async def get_my_packages(
    request: Request,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Номер страницы (начиная с 1)"),
    size: int = Query(10, ge=1, le=100, description="Размер страницы (от 1 до 100)"),
    type_id: Optional[int] = Query(None, description="Фильтр по типу посылки (ID типа)"),
    has_shipping_cost: Optional[bool] = Query(None, description="Фильтр по наличию рассчитанной стоимости доставки")
):
    session_id = request.state.session_id
    return await _get_user_packages(session_id, db, page, size, type_id, has_shipping_cost)


@package_router.get("/types", response_model=list[PackageGetTypes], tags=["Типы посылок"])
async def get_types_packages(db: AsyncSession = Depends(get_db)):
    """
    Получить все доступные типы посылок.

    Подробная документация доступна в README.md.
    """
    return await _get_all_packages_types(db)



@package_router.get("/{package_id}", response_model=PackageInfo, tags=["Посылки"])
async def get_package_info(package_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Получить детальную информацию о конкретной посылке.

    Посылка должна принадлежать текущей сессии пользователя.
    Подробная документация доступна в README.md.
    """
    session_id = request.state.session_id
    return await _get_package_info(package_id, session_id, db)
