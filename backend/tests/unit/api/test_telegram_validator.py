"""Unit-тесты проверки Telegram initData."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

import pytest

from app.api.auth.telegram_validator import validate_init_data
from app.core.config import settings
from app.core.exceptions import UnauthorizedException, ValidationException
from tests.unit.base import UnitTestCase


def _build_init_data(bot_token: str, user: dict, auth_date: int | None = None) -> str:
    payload = {
        "user": json.dumps(user, separators=(",", ":")),
        "auth_date": str(auth_date or int(time.time())),
    }
    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(payload.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    payload["hash"] = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()
    return urlencode(payload)


class TestTelegramValidator(UnitTestCase):
    @pytest.fixture(autouse=True)
    def _configure_bot_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(settings, "BOT_TOKEN", "123456:ABC-DEF")

    def test_validate_init_data_accepts_valid_signature(self) -> None:
        init_data = _build_init_data(
            settings.BOT_TOKEN,
            {"id": 42, "username": "vika", "first_name": "Vika", "language_code": "ru"},
        )
        user = validate_init_data(init_data)
        assert user.telegram_id == 42
        assert user.username == "vika"

    def test_validate_init_data_rejects_invalid_signature(self) -> None:
        init_data = _build_init_data(
            settings.BOT_TOKEN,
            {"id": 42, "username": "vika", "first_name": "Vika"},
        )
        tampered = init_data.replace("vika", "hacker")
        with pytest.raises(UnauthorizedException):
            validate_init_data(tampered)

    def test_validate_init_data_rejects_empty_payload(self) -> None:
        with pytest.raises(ValidationException):
            validate_init_data("")
