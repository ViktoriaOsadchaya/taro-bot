"""Unit-тесты внутренней аутентификации бота."""

from __future__ import annotations

import pytest

from app.api.access_control import verify_internal_token
from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from tests.unit.base import UnitTestCase


class TestAccessControl(UnitTestCase):
    @pytest.mark.asyncio
    async def test_verify_internal_token_accepts_secret_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(settings, "SECRET_KEY", "test-secret")
        monkeypatch.setattr(settings, "BOT_TOKEN", "")
        await verify_internal_token(x_internal_token="test-secret")

    @pytest.mark.asyncio
    async def test_verify_internal_token_rejects_invalid_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(settings, "SECRET_KEY", "test-secret")
        monkeypatch.setattr(settings, "BOT_TOKEN", "")
        with pytest.raises(UnauthorizedException):
            await verify_internal_token(x_internal_token="wrong-token")

    @pytest.mark.asyncio
    async def test_verify_internal_token_rejects_when_no_tokens_configured(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(settings, "SECRET_KEY", "")
        monkeypatch.setattr(settings, "BOT_TOKEN", "")
        with pytest.raises(UnauthorizedException):
            await verify_internal_token(x_internal_token="any-token")
