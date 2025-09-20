"""
Сервис для расчета стоимости доставки.

Содержит бизнес-логику расчета стоимости доставки с кешированием курсов валют.
"""

from src.config.settings import CACHE_KEY_PREFIX, CACHE_TTL
from src.external.cbr_api import fetch_usd_rub_rate
from src.utils.logging import get_logger
from src.utils.redis.redis_cache import cache

logger = get_logger(__name__)

CACHE_KEY = f"{CACHE_KEY_PREFIX}:usd_rub_rate"


async def get_usd_rub_rate() -> float:
    """
    Получить курс USD к RUB с кешированием.
    
    Returns:
        Курс USD к RUB
    """
    # Пытаемся получить из кеша
    cached_rate = await cache.get(CACHE_KEY)
    if cached_rate is not None:
        logger.debug("Курс получен из кеша")
        return float(cached_rate)
    
    # Если в кеше нет, получаем от API
    logger.info("Получение курса от API ЦБ РФ")
    rate = await fetch_usd_rub_rate()
    
    # Сохраняем в кеш
    await cache.set(CACHE_KEY, rate, CACHE_TTL)
    logger.info(f"Курс сохранен в кеш на {CACHE_TTL} секунд")
    
    return rate


def calculate_shipping_cost(weight: float, price: float, usd_rate: float) -> str:
    """
    Рассчитать стоимость доставки.
    
    Формула: ((Вес × 0.5) + (Цена × 0.01)) × Курс USD/RUB
    
    Args:
        weight: Вес посылки в кг
        price: Цена посылки в рублях
        usd_rate: Курс USD к RUB
        
    Returns:
        Стоимость доставки в рублях (строка)
    """
    base_cost = (weight * 0.5) + (price * 0.01)
    shipping_cost = base_cost * usd_rate
    return f"{shipping_cost:.2f}"


async def clear_usd_rub_cache():
    """Очистить кеш курса USD/RUB."""
    try:
        await cache.get_client()
        client = await cache.get_client()
        await client.delete(CACHE_KEY)
        logger.info("Кеш курса USD/RUB очищен")
    except Exception as e:
        logger.error(f"Ошибка очистки кеша: {e}")
