import json
from typing import Any, Optional

from redis.asyncio import Redis

from dostavka.core.logging import get_logger
from dostavka.settings import REDIS_URL

# Получаем логгер для модуля
logger = get_logger(__name__)

class RedisCache:
    def __init__(self, redis_url: str = REDIS_URL):
        self.redis_url = redis_url
        self._client: Optional[Redis] = None

    async def get_client(self) -> Redis:
        """Получить Redis клиент"""
        if self._client is None:
            self._client = Redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return self._client

    async def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        try:
            client = await self.get_client()
            value = await client.get(key)
            if value:
                logger.debug(f"Значение получено из кэша: {key}")
                return json.loads(value)
            else:
                logger.debug(f"Ключ не найден в кэше: {key}")
                return None
        except Exception as e:
            logger.error(f"Ошибка получения значения из кэша {key}: {e}")
            return None

    async def set(self, key: str, value: Any, expire_seconds: int = 3600) -> bool:
        """Установить значение в кэш с TTL"""
        try:
            client = await self.get_client()
            await client.setex(key, expire_seconds, json.dumps(value))
            logger.debug(f"Значение установлено в кэш: {key}, TTL: {expire_seconds} сек")
            return True
        except Exception as e:
            logger.error(f"Ошибка установки значения в кэш {key}: {e}")
            return False

    async def close(self):
        """Закрыть соединение"""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Соединение с Redis закрыто")


# Глобальный экземпляр кэша
cache = RedisCache()
