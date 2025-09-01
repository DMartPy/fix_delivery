import asyncio

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dostavka.core.logging import get_logger
from dostavka.db.models import Package
from dostavka.services.ship_price import calculate_ship
from dostavka.settings import REAL_DATABASE_URL

from .celery_app import celery_app

# Получаем логгер для модуля
logger = get_logger(__name__)

sync_engine = create_engine(REAL_DATABASE_URL.replace("+asyncpg", "+psycopg2"))
SyncSession = sessionmaker(bind=sync_engine)

async def _calculate_shipping_cost(weight: float, price: float):
    return await calculate_ship(weight, price)

def _update_package_shipping_cost(package_id: str, shipping_cost: float):
    """Синхронная функция для обновления стоимости доставки"""
    session = SyncSession()
    try:
        package = session.query(Package).filter(Package.id == package_id).first()
        if package:
            package.shipping_cost = str(shipping_cost)  # Преобразуем в строку
            session.commit()
            logger.info(f"Пакет обновлен с ID: {package.id}, стоимость доставки: {shipping_cost}")
            return package.id
        else:
            logger.warning(f"Пакет с ID {package_id} не найден")
            return None
    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка при обновлении пакета: {e}")
        raise
    finally:
        session.close()

@celery_app.task(name="dostavka.celery.tasks.calculate_and_save")
def calculate_and_save(package_data: dict):
    logger.info(f"Начинаем расчет стоимости доставки для пакета {package_data['id']}")
    try:
        shipping_cost = asyncio.run(_calculate_shipping_cost(package_data["weight"], package_data["price"]))
        logger.info(f"Стоимость доставки рассчитана: {shipping_cost}")
        result = _update_package_shipping_cost(package_data["id"], shipping_cost)
        logger.info(f"Задача выполнена успешно для пакета {package_data['id']}")
        return result
    except Exception as e:
        logger.error(f"Ошибка в задаче Celery: {e}", exc_info=True)
        raise
