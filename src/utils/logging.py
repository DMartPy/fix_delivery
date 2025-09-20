"""
Настройка логирования для приложения.
"""

import logging
import sys
from pathlib import Path

from src.config.settings import LOG_FORMAT, LOG_LEVEL


def setup_logging():
    """Настроить логирование для приложения."""
    # Создаем директорию для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Настраиваем корневой логгер
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper()),
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "dostavka.log", encoding="utf-8")
        ]
    )


def get_logger(name: str) -> logging.Logger:
    """Получить логгер для модуля."""
    return logging.getLogger(name)
