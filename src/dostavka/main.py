from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from dostavka.api.handlers import package_router
from dostavka.api.session_middleware import SessionMiddleware
from dostavka.core.logging import get_logger, setup_logging
from dostavka.db.init_db import create_tables, init_package_types
from dostavka.redis.redis_cache import cache
from dostavka.services.ship_price import fetch_usd_rub_rate

# Инициализируем логирование
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Запуск приложения...")
        await create_tables()
        logger.info("Таблицы созданы")

        logger.info("Начинаю инициализацию типов посылок...")
        await init_package_types()
        logger.info("Типы посылок инициализированы")

        logger.info("Инициализация Redis кеша...")
        try:
            await fetch_usd_rub_rate()
            logger.info("Курс доллара к рублю загружен в кеш")
        except Exception as e:
            logger.error(f"Ошибка загрузки курса в кеш: {e}")
        logger.info("Redis кеш инициализирован")

        logger.info("Приложение готово к работе!")
        yield
    except Exception as e:
        logger.error(f"Критическая ошибка в lifespan: {e}", exc_info=True)
        raise
    finally:
        logger.info("Завершение lifespan")
        await cache.close()




app = FastAPI(
    title="Dostavka API",
    description="""
    ## 🚚 API для системы доставки посылок
    
    ### Основные возможности:
    - **Создание посылок** с автоматическим расчетом стоимости доставки
    - **Управление посылками** с пагинацией и фильтрацией
    - **Асинхронная обработка** через Celery и RabbitMQ
    - **Кеширование курсов валют** в Redis
    
    ### Архитектура:
    - **FastAPI** - веб-фреймворк
    - **PostgreSQL** - основная база данных
    - **Redis** - кеширование курсов валют
    - **RabbitMQ** - очередь сообщений
    - **Celery** - асинхронные задачи
    
    ### Особенности:
    - Автоматический расчет стоимости доставки на основе веса и цены
    - Использование актуального курса USD/RUB от ЦБ РФ
    - Пагинация и фильтрация для удобной работы с большими объемами данных
    """,
    lifespan=lifespan
)

app.add_middleware(SessionMiddleware)
main_api_router = APIRouter()
main_api_router.include_router(package_router, prefix="/packages", tags=["Посылки"])
app.include_router(main_api_router)

if __name__=="__main__":
    uvicorn.run(app, host='localhost', port=8000)
