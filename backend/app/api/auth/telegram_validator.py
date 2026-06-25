"""
Проверка подписи Telegram WebApp initData.

Алгоритм: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from urllib.parse import parse_qsl

from app.core.config import settings
from app.core.exceptions import UnauthorizedException, ValidationException


@dataclass(frozen=True, slots=True)
class TelegramUserData:
    """Данные пользователя из проверенного initData."""

    telegram_id: int
    username: str | None
    first_name: str | None
    language_code: str


def validate_init_data(init_data: str, *, max_age_seconds: int = 86400) -> TelegramUserData:
    """
    Проверяет HMAC-SHA256 подпись initData и извлекает профиль пользователя.

    ***init_data: строка window.Telegram.WebApp.initData***
    """
    if not init_data or not init_data.strip():
        raise ValidationException("init_data не может быть пустым")

    if not settings.BOT_TOKEN:
        raise UnauthorizedException("BOT_TOKEN не настроен")

    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise ValidationException("init_data не содержит hash")

    auth_date_raw = parsed.get("auth_date")
    if auth_date_raw is None:
        raise ValidationException("init_data не содержит auth_date")

    try:
        auth_date = int(auth_date_raw)
    except ValueError as exc:
        raise ValidationException("Некорректный auth_date в init_data") from exc

    if time.time() - auth_date > max_age_seconds:
        raise UnauthorizedException("init_data устарел")

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(parsed.items()))
    secret_key = hmac.new(
        b"WebAppData",
        settings.BOT_TOKEN.encode(),
        hashlib.sha256,
    ).digest()
    computed_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        raise UnauthorizedException("Невалидная подпись init_data")

    user_raw = parsed.get("user")
    if not user_raw:
        raise ValidationException("init_data не содержит user")

    try:
        user_payload = json.loads(user_raw)
        telegram_id = int(user_payload["id"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValidationException("Некорректный объект user в init_data") from exc

    if telegram_id < 1:
        raise ValidationException("Некорректный telegram_id в init_data")

    return TelegramUserData(
        telegram_id=telegram_id,
        username=user_payload.get("username"),
        first_name=user_payload.get("first_name"),
        language_code=user_payload.get("language_code") or "ru",
    )
