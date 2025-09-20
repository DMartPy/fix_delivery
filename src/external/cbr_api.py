"""
Модуль для работы с внешними API.

Содержит функции для получения курсов валют.
"""

import aiohttp
import json
from src.config.settings import CBR_API_TIMEOUT, CBR_API_URL
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def fetch_usd_rub_rate(timeout: float = CBR_API_TIMEOUT) -> float:
    """
    Получить курс USD к RUB от ЦБ РФ.
    
    Args:
        timeout: Таймаут запроса в секундах
        
    Returns:
        Курс USD к RUB
        
    Raises:
        Exception: При ошибке получения курса
    """
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.get(CBR_API_URL) as response:
                if response.status == 200:
                    text = await response.text()
                    data = json.loads(text)
                    
                    usd_rate = data["Valute"]["USD"]["Value"]
                    logger.info(f"Получен курс USD/RUB: {usd_rate}")
                    return float(usd_rate)
                else:
                    raise Exception(f"Ошибка API ЦБ: статус {response.status}")
    except Exception as e:
        logger.error(f"Ошибка получения курса USD/RUB: {e}")
        raise
