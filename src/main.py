import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import APP_NAME, APP_VERSION, DEBUG
from src.db.init_db import create_tables, init_package_types
from src.middleware.sessions import SessionMiddleware
from src.routes.handlers import package_router
from src.services.shipping import get_usd_rub_rate
from src.utils.logging import get_logger, setup_logging
from src.utils.redis.redis_cache import cache

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
            await get_usd_rub_rate()
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
    title=APP_NAME,
    version=APP_VERSION,
    description="API для системы доставки посылок с автоматическим расчетом стоимости доставки. Подробная документация доступна в README.md.",
    debug=DEBUG,
    lifespan=lifespan
)

app.add_middleware(SessionMiddleware)
main_api_router = APIRouter()
main_api_router.include_router(package_router, prefix="/packages", tags=["Посылки"])
app.include_router(main_api_router)

if __name__=="__main__":
    uvicorn.run(app, host='localhost', port=8000)
