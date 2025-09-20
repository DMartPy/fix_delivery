import asyncio

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import CELERY_DATABASE_URL
from src.models.db import Package
from src.services.shipping import calculate_shipping_cost
from src.utils.logging import get_logger

from .celery_app import celery_app

# Получаем логгер для модуля
logger = get_logger(__name__)


@celery_app.task
def calculate_and_save(package_id: str):
    """
    Рассчитать стоимость доставки и сохранить в базу данных.
    
    Args:
        package_id: ID посылки
    """
    try:
        logger.info(f"Начинаю расчет стоимости для посылки {package_id}")
        
        # Создаем синхронное соединение с БД для Celery
        engine = create_engine(CELERY_DATABASE_URL)
        Session = sessionmaker(bind=engine)
        
        with Session() as session:
            # Получаем посылку
            package = session.query(Package).filter(Package.id == package_id).first()
            if not package:
                logger.error(f"Посылка {package_id} не найдена")
                return
            
            # Получаем курс USD/RUB
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                from src.services.shipping import get_usd_rub_rate
                usd_rate = loop.run_until_complete(get_usd_rub_rate())
            finally:
                loop.close()
            
            # Рассчитываем стоимость доставки
            shipping_cost = calculate_shipping_cost(
                package.weight, 
                package.price, 
                usd_rate
            )
            
            # Обновляем посылку
            package.shipping_cost = shipping_cost
            session.commit()
            
            logger.info(f"Стоимость доставки для посылки {package_id}: {shipping_cost}")
            
    except Exception as e:
        logger.error(f"Ошибка расчета стоимости для посылки {package_id}: {e}")
        raise
