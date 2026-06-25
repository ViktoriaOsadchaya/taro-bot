"""
FastAPI-зависимости JWT-авторизации.

Используются на защищённых роутерах и в эндпоинтах, где нужен текущий пользователь.
"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.auth.jwt_utils import decode_access_token
from app.api.schemas.user_dto import UserReadDTO

http_bearer = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
) -> UserReadDTO:
    """
    Извлекает и проверяет JWT из Authorization: Bearer <token>.

    Возвращает UserReadDTO из claims токена.
    """
    return decode_access_token(credentials.credentials)


CURRENT_USER = Depends(get_current_user)
