import os
from typing import Optional

from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()


def get_env(key: str, default: Optional[str] = None) -> str:
    """Получить переменную окружения с fallback значением."""
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Переменная окружения {key} не установлена")
    return value


def get_bool_env(key: str, default: bool = False) -> bool:
    """Получить булеву переменную окружения."""
    value = os.getenv(key, str(default)).lower()
    return value in ("true", "1", "yes", "on")


def get_int_env(key: str, default: int) -> int:
    """Получить целочисленную переменную окружения."""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


# База данных
DATABASE_URL = get_env("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres")
REAL_DATABASE_URL = DATABASE_URL  # Для совместимости

# Синхронный URL для Celery
CELERY_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

# Redis
REDIS_URL = get_env("REDIS_URL", "redis://localhost:6379")

# RabbitMQ
RABBITMQ_URL = get_env("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

# Настройки приложения
APP_NAME = get_env("APP_NAME", "Dostavka API")
APP_VERSION = get_env("APP_VERSION", "0.1.0")
DEBUG = get_bool_env("DEBUG", False)

# Логирование
LOG_LEVEL = get_env("LOG_LEVEL", "INFO")
LOG_FORMAT = get_env("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Внешние API
CBR_API_URL = get_env("CBR_API_URL", "https://www.cbr-xml-daily.ru/daily_json.js")
CBR_API_TIMEOUT = get_int_env("CBR_API_TIMEOUT", 5)

# Кеширование
CACHE_TTL = get_int_env("CACHE_TTL", 3600)
CACHE_KEY_PREFIX = get_env("CACHE_KEY_PREFIX", "dostavka")

# Сессии
SESSION_COOKIE_NAME = get_env("SESSION_COOKIE_NAME", "session_id")
SESSION_MAX_AGE = get_int_env("SESSION_MAX_AGE", 2592000)  # 30 дней

# Celery
CELERY_BROKER_URL = get_env("CELERY_BROKER_URL", RABBITMQ_URL)
CELERY_RESULT_BACKEND = get_env("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")