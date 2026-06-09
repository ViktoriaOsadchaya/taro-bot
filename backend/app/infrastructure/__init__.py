"""Инфраструктурные адаптеры (Redis, LLM) — не БД и не HTTP."""

from app.infrastructure.llm_client import LlmClient
from app.infrastructure.reading_session_store import ReadingSessionStore

__all__ = ["LlmClient", "ReadingSessionStore"]
