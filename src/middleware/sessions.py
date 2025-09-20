"""
Middleware для управления сессиями пользователей.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.config.settings import SESSION_COOKIE_NAME, SESSION_MAX_AGE


class SessionMiddleware(BaseHTTPMiddleware):
    """
    Middleware для управления сессиями пользователей.
    
    Автоматически создает сессию для каждого нового пользователя
    и добавляет session_id в состояние запроса.
    """
    
    async def dispatch(self, request: Request, call_next):
        """Обработать запрос с управлением сессией."""
        try:
            # Получаем session_id из cookies
            session_id = request.cookies.get(SESSION_COOKIE_NAME)
            
            if not session_id:
                # Создаем новую сессию
                import uuid
                session_id = str(uuid.uuid4())
            
            # Добавляем session_id в состояние запроса
            request.state.session_id = session_id
            
            # Обрабатываем запрос
            response = await call_next(request)
            
            # Устанавливаем cookie с session_id
            response.set_cookie(
                key=SESSION_COOKIE_NAME,
                value=session_id,
                max_age=SESSION_MAX_AGE,
                httponly=True,
                secure=False,  # В продакшене должно быть True
                samesite="lax"
            )
            
            return response
            
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": {"message": f"Ошибка в SessionMiddleware: {str(e)}"}}
            )
