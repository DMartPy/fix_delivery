
import aiohttp

from dostavka.core.logging import get_logger
from dostavka.redis.redis_cache import cache

# Получаем логгер для модуля
logger = get_logger(__name__)

CBR_DAILY_URL = "https://www.cbr-xml-daily.ru/daily_json.js"
CACHE_KEY = "usd_rub_rate"
CACHE_TTL = 3600  # 1 час


async def fetch_usd_rub_rate(timeout: float = 5, use_cache: bool = True) -> float:
    if use_cache and (rate := await cache.get(CACHE_KEY)):
        logger.debug(f"Курс USD/RUB получен из кеша: {rate}")
        return float(rate)

    logger.info("Получаем актуальный курс USD/RUB от ЦБ РФ")
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as s:
        async with s.get(CBR_DAILY_URL) as r:
            r.raise_for_status()
            rate = float((await r.json())["Valute"]["USD"]["Value"])
            logger.info(f"Получен курс USD/RUB: {rate}")

    if use_cache:
        await cache.set(CACHE_KEY, rate, CACHE_TTL)
        logger.info(f"Курс USD/RUB сохранен в кеш на {CACHE_TTL} секунд")
    return rate


async def clear_usd_rub_cache() -> bool:
    try:
        client = await cache.get_client()
        await client.delete(CACHE_KEY)
        logger.info("Кэш курса USD/RUB очищен")
        return True
    except Exception as e:
        logger.error(f"Ошибка очистки кэша: {e}")
        return False


async def calculate_ship(weight, price) -> float:
    logger.info(f"Рассчитываем стоимость доставки: вес={weight}кг, цена={price}руб")
    rate = await fetch_usd_rub_rate()
    cost = float(((weight * 0.5) + (price * 0.01)) * rate)
    logger.info(f"Стоимость доставки рассчитана: {cost} руб (курс USD/RUB: {rate})")
    return cost

