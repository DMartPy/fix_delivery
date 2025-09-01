from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from dostavka.api.models import (
    PackageCreate,
    PackageGetTypes,
    PackageInfo,
    PaginatedPackagesResponse,
    TaskResponse,
)
from dostavka.celery.tasks import calculate_and_save
from dostavka.core.logging import get_logger
from dostavka.db.dals import PackageDAL, SessionDAL
from dostavka.db.session import AsyncSession, get_db
from dostavka.services.check_session import check_session

# Получаем логгер для модуля
logger = get_logger(__name__)


package_router = APIRouter()


async def _create_new_package(body: PackageCreate, session_id: str, db):
    async with db as session:
        async with session.begin():
            package_dal = PackageDAL(session)
            session_dal = SessionDAL(session)

            # Проверяем сессию
            try:
                check_session(session_id, package_dal, session_dal)
            except Exception:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "FORBIDDEN",
                        "message": "Недействительная сессия",
                        "details": {"session_id": session_id}
                    }
                )

            # Проверяем существование типа посылки
            package_type = await package_dal.get_package_type_by_id(body.type_id)
            if not package_type:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "NOT_FOUND",
                        "message": "Тип посылки не найден",
                        "details": {"type_id": body.type_id}
                    }
                )

            try:
                package = await package_dal.create_package(
                    name=body.name,
                    weight=body.weight,
                    type_id=body.type_id,
                    price=body.price,
                    session_id=session_id,
                    shipping_cost="Не рассчитано"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "INTERNAL_SERVER_ERROR",
                        "message": "Ошибка создания посылки",
                        "details": {"original_error": str(e)}
                    }
                )

            package_data = {
                "id": str(package.id),
                "name": package.name,
                "weight": package.weight,
                "type_id": body.type_id,
                "price": body.price,
                "session_id": session_id
            }

            try:
                logger.info(f"Отправляем задачу в Celery для пакета {package.id}")
                task = calculate_and_save.delay(package_data)
                logger.info(f"Задача отправлена в Celery с ID: {task.id}")
                return TaskResponse(task_id=task.id, status="processing")
            except Exception as e:
                # Если не удалось отправить в Celery, все равно возвращаем созданную посылку
                logger.error(f"Ошибка отправки в Celery: {e}")
                return TaskResponse(task_id="celery_error", status="error")


async def _get_user_packages(
    session_id: str,
    db,
    page: int = 1,
    size: int = 10,
    type_id: Optional[int] = None,
    has_shipping_cost: Optional[bool] = None
):
    async with db as session:
        async with session.begin():
            package_dal = PackageDAL(session)
            session_dal = SessionDAL(session)

            # Проверяем сессию
            try:
                check_session(session_id, package_dal, session_dal)
            except Exception:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "FORBIDDEN",
                        "message": "Недействительная сессия",
                        "details": {"session_id": session_id}
                    }
                )

            # Проверяем существование типа посылки, если указан
            if type_id:
                package_type = await package_dal.get_package_type_by_id(type_id)
                if not package_type:
                    raise HTTPException(
                        status_code=404,
                        detail={
                            "error": "NOT_FOUND",
                            "message": "Тип посылки не найден",
                            "details": {"type_id": type_id}
                        }
                    )

            try:
                packages, total = await package_dal.get_packages_by_session_with_filters(
                    session_id=session_id,
                    page=page,
                    size=size,
                    type_id=type_id,
                    has_shipping_cost=has_shipping_cost
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "INTERNAL_SERVER_ERROR",
                        "message": "Ошибка получения посылок",
                        "details": {"original_error": str(e)}
                    }
                )

            pages = (total + size - 1) // size

            return {
                "packages": packages,
                "total": total,
                "page": page,
                "size": size,
                "pages": pages
            }


async def _get_all_packages_types(db):
    async with db as session:
        async with session.begin():
            package_dal = PackageDAL(session)
            try:
                types = await package_dal.get_packeges_all_type()
                return types
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "INTERNAL_SERVER_ERROR",
                        "message": "Ошибка получения типов посылок",
                        "details": {"original_error": str(e)}
                    }
                )


async def _get_package_info(id, session_id: str, db):
        async with db as session:
            async with session.begin():
                package_dal = PackageDAL(session)

                # Проверяем сессию
                try:
                    check_session(session_id, package_dal, None)  # Не нужен session_dal для этой проверки
                except Exception:
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "error": "FORBIDDEN",
                            "message": "Недействительная сессия",
                            "details": {"session_id": session_id}
                        }
                    )

                try:
                    package = await package_dal.get_package_by_id_and_session(id, session_id)
                    if not package:
                        raise HTTPException(
                            status_code=404,
                            detail={
                                "error": "NOT_FOUND",
                                "message": "Посылка не найдена",
                                "details": {"package_id": id, "session_id": session_id}
                            }
                        )

                    return PackageInfo(
                        id = package.id,
                        name = package.name,
                        weight = package.weight,
                        type_id = package.type_id,
                        price = package.price,
                        shipping_cost = package.shipping_cost
                    )
                except HTTPException:
                    raise
                except Exception as e:
                    raise HTTPException(
                        status_code=500,
                        detail={
                            "error": "INTERNAL_SERVER_ERROR",
                            "message": "Ошибка получения информации о посылке",
                            "details": {"original_error": str(e)}
                        }
                    )



@package_router.post("/", response_model=TaskResponse, tags=["Посылки"])
async def create_package(body: PackageCreate, request: Request, db: AsyncSession = Depends(get_db)) -> TaskResponse:
    """
    Создать новую посылку для текущей сессии
    
    ## Описание
    Создает новую посылку и отправляет задачу в Celery для расчета стоимости доставки.
    Изначально `shipping_cost` устанавливается как "Не рассчитано".
    
    ## Процесс
    1. Создается запись в базе данных
    2. Задача отправляется в RabbitMQ
    3. Celery worker рассчитывает стоимость доставки
    4. База данных обновляется с рассчитанной стоимостью
    
    ## Возвращает
    - **task_id**: ID задачи в Celery
    - **status**: Статус обработки ("processing")
    
    ## Пример запроса
    ```json
    {
        "name": "Электроника",
        "weight": 2.5,
        "type_id": 1,
        "price": 15000.0
    }
    ```
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
    """
    Получить посылки текущей сессии с пагинацией и фильтрацией
    
    ## Описание
    Возвращает список посылок для текущей сессии с поддержкой пагинации и фильтрации.
    
    ## Параметры запроса
    
    ### Пагинация
    - **page**: Номер страницы (начиная с 1)
    - **size**: Размер страницы (от 1 до 100)
    
    ### Фильтры
    - **type_id**: ID типа посылки для фильтрации
    - **has_shipping_cost**: 
        - `true` - только посылки с рассчитанной стоимостью
        - `false` - только посылки без рассчитанной стоимости  
        - `null` - все посылки (по умолчанию)
    
    ## Примеры запросов
    
    ### Базовая пагинация
    ```
    GET /packages/?page=1&size=10
    ```
    
    ### Фильтр по типу
    ```
    GET /packages/?type_id=1&page=1&size=20
    ```
    
    ### Фильтр по стоимости доставки
    ```
    GET /packages/?has_shipping_cost=true&page=1&size=15
    ```
    
    ### Комбинированные фильтры
    ```
    GET /packages/?type_id=2&has_shipping_cost=false&page=2&size=25
    ```
    
    ## Возвращает
    - **packages**: Список посылок
    - **total**: Общее количество посылок
    - **page**: Текущая страница
    - **size**: Размер страницы
    - **pages**: Общее количество страниц
    """
    session_id = request.state.session_id
    return await _get_user_packages(session_id, db, page, size, type_id, has_shipping_cost)


@package_router.get("/types", response_model=list[PackageGetTypes], tags=["Типы посылок"])
async def get_types_packages(db: AsyncSession = Depends(get_db)):
    """
    Получить все доступные типы посылок
    
    ## Описание
    Возвращает список всех типов посылок, доступных в системе.
    Эти типы используются при создании новых посылок.
    
    ## Возвращает
    Список объектов с полями:
    - **id**: Уникальный идентификатор типа
    - **name**: Название типа посылки
    - **description**: Описание типа посылки
    
    ## Пример ответа
    ```json
    [
        {
            "id": 1,
            "name": "Электроника",
            "description": "Электронные устройства и гаджеты"
        },
        {
            "id": 2,
            "name": "Одежда",
            "description": "Одежда и обувь"
        }
    ]
    ```
    """
    return await _get_all_packages_types(db)



@package_router.get("/{package_id}", response_model=PackageInfo, tags=["Посылки"])
async def get_package_info(package_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Получить детальную информацию о конкретной посылке
    
    ## Описание
    Возвращает полную информацию о посылке по её ID.
    Посылка должна принадлежать текущей сессии пользователя.
    
    ## Параметры пути
    - **package_id**: UUID посылки
    
    ## Возвращает
    Объект посылки с полями:
    - **id**: Уникальный идентификатор посылки
    - **name**: Название посылки
    - **weight**: Вес в кг
    - **type_id**: ID типа посылки
    - **price**: Стоимость товара в рублях
    - **shipping_cost**: Стоимость доставки (может быть "Не рассчитано" или числовое значение)
    
    ## Пример ответа
    ```json
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "iPhone 15",
        "weight": 0.2,
        "type_id": 1,
        "price": 89990.0,
        "shipping_cost": "1349.85"
    }
    ```
    
    ## Ошибки
    - **404**: Посылка не найдена
    - **403**: Посылка не принадлежит текущей сессии
    """
    session_id = request.state.session_id
    return await _get_package_info(package_id, session_id, db)

