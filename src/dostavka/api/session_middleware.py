import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class SessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, session_cookie_name: str = "session_id"):
        super().__init__(app)
        self.session_cookie_name = session_cookie_name

    async def dispatch(self, request: Request, call_next):
        try:
            session_id = request.cookies.get(self.session_cookie_name)
            if not session_id or not self._is_valid_uuid(session_id):
                session_id = str(uuid.uuid4())

            request.state.session_id = session_id

            response = await call_next(request)

            if not request.cookies.get(self.session_cookie_name):
                response.set_cookie(
                    key=self.session_cookie_name,
                    value=session_id,
                    max_age=30 * 24 * 60 * 60,
                    httponly=True,
                    secure=False,
                    samesite="lax"
                )

            return response
        except Exception as e:
            print(f"Ошибка в SessionMiddleware: {e}")
            import traceback
            traceback.print_exc()

            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error in middleware"}
            )

    def _is_valid_uuid(self, uuid_string: str) -> bool:
        """Проверяет, является ли строка валидным UUID"""
        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False
