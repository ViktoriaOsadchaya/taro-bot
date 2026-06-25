"""FastAPI dependencies для API-слоя."""

from app.api.deps.auth_deps import CURRENT_USER, get_current_user

__all__ = ["CURRENT_USER", "get_current_user"]
