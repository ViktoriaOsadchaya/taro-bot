"""
Зависимости аутентификации для внутреннего API бота.

Бот передаёт X-Internal-Token (SECRET_KEY или BOT_TOKEN) и X-Telegram-Id пользователя.
"""

from typing import Annotated

from fastapi import Header

from app.core.config import settings
from app.core.exceptions import UnauthorizedException


def _allowed_internal_tokens() -> set[str]:
    """Собирает допустимые токены из конфигурации."""
    tokens: set[str] = set()
    if settings.SECRET_KEY:
        tokens.add(settings.SECRET_KEY)
    if settings.BOT_TOKEN:
        tokens.add(settings.BOT_TOKEN)
    return tokens


async def verify_internal_token(
    x_internal_token: Annotated[str, Header(alias="X-Internal-Token")],
) -> None:
    """
    Проверяет заголовок X-Internal-Token.

    Используется как dependency на защищённых роутерах.
    """
    allowed = _allowed_internal_tokens()
    if not allowed or x_internal_token not in allowed:
        raise UnauthorizedException("Неверный или отсутствующий X-Internal-Token")


async def get_telegram_id(
    x_telegram_id: Annotated[int, Header(alias="X-Telegram-Id", ge=1)],
) -> int:
    """
    Извлекает Telegram ID пользователя из заголовка X-Telegram-Id.

    Обязателен для endpoints, привязанных к сессии или истории раскладов.
    """
    return x_telegram_id
