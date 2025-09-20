"""
Сервис для работы с сессиями пользователей.
"""

from src.repositories.sessions import SessionRepository


async def check_session(session_id: str, package_repository, session_repository: SessionRepository):
    """
    Проверяет существование сессии и создает новую при необходимости.
    
    Args:
        session_id: ID сессии
        package_repository: Репозиторий посылок
        session_repository: Репозиторий сессий
        
    Returns:
        Объект сессии
    """
    session = await session_repository.get_by_id(session_id)
    
    if not session:
        # Создаем новую сессию
        session = await session_repository.create(session_id)
    
    return session
