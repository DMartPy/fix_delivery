import logging
import sys
from pathlib import Path


def setup_logging():
    """Простая настройка логирования"""

    # Создаем директорию для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Настраиваем форматирование
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Хендлер для файла
    file_handler = logging.FileHandler(
        'logs/dostavka.log',
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    # Хендлер для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Настраиваем логгеры для разных модулей
    logging.getLogger('dostavka').setLevel(logging.INFO)
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('celery').setLevel(logging.INFO)

    logging.info("Логирование настроено")


def get_logger(name: str) -> logging.Logger:
    """Получить логгер"""
    return logging.getLogger(name)
