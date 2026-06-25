"""
Создание и проверка JWT access-токенов.

Используется после успешной авторизации через Telegram WebApp initData.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from app.api.schemas.user_dto import UserReadDTO
from app.core.config import settings
from app.core.exceptions import UnauthorizedException

JWT_SUBJECT_USER = "user"


def create_access_token(user: UserReadDTO) -> str:
    """
    Создаёт JWT access-токен для авторизованного пользователя.

    ***user: сохранённый профиль после upsert***
    """
    if not settings.SECRET_KEY:
        raise UnauthorizedException("SECRET_KEY не настроен")

    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict[str, Any] = {
        "sub": str(user.primary_key),
        "type": JWT_SUBJECT_USER,
        "telegram_id": user.telegram_id,
        "username": user.username,
        "first_name": user.first_name,
        "language_code": user.language_code,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> UserReadDTO:
    """
    Проверяет подпись JWT и возвращает UserReadDTO из claims.

    ***token: строка из заголовка Authorization Bearer***
    """
    if not settings.SECRET_KEY:
        raise UnauthorizedException("SECRET_KEY не настроен")

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except jwt.ExpiredSignatureError as exc:
        raise UnauthorizedException("JWT-токен истёк") from exc
    except jwt.InvalidTokenError as exc:
        raise UnauthorizedException("Невалидный JWT-токен") from exc

    if payload.get("type") != JWT_SUBJECT_USER:
        raise UnauthorizedException("Неверный тип JWT-токена")

    try:
        return UserReadDTO(
            primary_key=int(payload["sub"]),
            telegram_id=int(payload["telegram_id"]),
            username=payload.get("username"),
            first_name=payload.get("first_name"),
            language_code=payload.get("language_code", "ru"),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise UnauthorizedException("JWT-токен содержит некорректные данные") from exc
