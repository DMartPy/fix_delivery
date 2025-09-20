"""
Базовые схемы для всех моделей.
"""

from pydantic import BaseModel


class TunedModel(BaseModel):
    """Базовая модель с настройками для JSON."""
    
    class Config:
        from_attributes = True
