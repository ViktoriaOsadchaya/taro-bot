"""Unit-тесты JWT-авторизации."""

from __future__ import annotations

import pytest

from app.api.auth.jwt_utils import create_access_token, decode_access_token
from app.api.schemas.user_dto import UserReadDTO
from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from tests.unit.base import UnitTestCase


class TestJwtUtils(UnitTestCase):
    @pytest.fixture(autouse=True)
    def _configure_secret(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(settings, "SECRET_KEY", "test-secret-key")
        monkeypatch.setattr(settings, "ALGORITHM", "HS256")
        monkeypatch.setattr(settings, "JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 60)

    def test_create_and_decode_access_token(self) -> None:
        user = UserReadDTO(
            primary_key=1,
            telegram_id=123456,
            username="vika",
            first_name="Vika",
            language_code="ru",
        )
        token = create_access_token(user)
        decoded = decode_access_token(token)
        assert decoded.primary_key == user.primary_key
        assert decoded.telegram_id == user.telegram_id
        assert decoded.username == user.username

    def test_decode_access_token_rejects_invalid_token(self) -> None:
        with pytest.raises(UnauthorizedException):
            decode_access_token("invalid.token.value")
