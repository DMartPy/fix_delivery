"""
Репозиторий для работы с сессиями в базе данных.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select

from src.db.session import AsyncSession
from src.models.db import Session


class SessionRepository:
    """
    Репозиторий для работы с сессиями в базе данных.
    
    Содержит методы для CRUD операций с сессиями.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, session_id: str) -> Optional[Session]:
        """Получить сессию по ID."""
        result = await self.session.execute(
            select(Session).where(Session.id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, session_id: str) -> Session:
        """Создать новую сессию."""
        session = Session(
            id=uuid.UUID(session_id),
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
        self.session.add(session)
        await self.session.commit()
        await self.session.refresh(session)
        return session
    
    async def update_activity(self, session_id: str) -> Optional[Session]:
        """Обновить время последней активности сессии."""
        session = await self.get_by_id(session_id)
        if session:
            session.last_activity = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(session)
        return session
