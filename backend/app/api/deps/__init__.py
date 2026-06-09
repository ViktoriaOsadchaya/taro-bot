"""FastAPI dependencies для API-слоя."""

from app.api.deps.bot_auth import get_telegram_id, verify_internal_token

__all__ = ["get_telegram_id", "verify_internal_token"]
