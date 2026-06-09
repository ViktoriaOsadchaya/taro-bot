"""
Хранилище активных сессий расклада в Redis.

Не является репозиторием БД: работает только с ключами reading_session:{telegram_id}.
"""

import os

from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from app.api.schemas.reading_session_dto import ReadingSessionDTO
from app.core.exceptions import ExternalServiceException

# TTL сессии в секундах (30 минут).
READING_SESSION_TTL_SECONDS = int(os.getenv("READING_SESSION_TTL_SECONDS", "1800"))


class ReadingSessionStore:
    """
    CRUD для Redis-сессий расклада.

    Используется ReadingSessionService для пошагового вытягивания карт
    до финализации и сохранения в PostgreSQL.
    """

    KEY_PREFIX = "reading_session:"

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    def _key(self, telegram_id: int) -> str:
        """Формирует ключ Redis по Telegram ID пользователя."""
        return f"{self.KEY_PREFIX}{telegram_id}"

    async def get(self, telegram_id: int) -> ReadingSessionDTO | None:
        """Возвращает активную сессию или None, если расклад не начат."""
        try:
            raw = await self.redis.get(self._key(telegram_id))
        except Exception as exc:
            raise ExternalServiceException("Redis недоступен") from exc
        if raw is None:
            return None
        return ReadingSessionDTO.model_validate_json(raw)

    async def save(self, telegram_id: int, session: ReadingSessionDTO) -> None:
        """Сохраняет сессию с TTL; перезаписывает предыдущую при новом раскладе."""
        try:
            await self.redis.set(
                self._key(telegram_id),
                session.model_dump_json(),
                ex=READING_SESSION_TTL_SECONDS,
            )
        except Exception as exc:
            raise ExternalServiceException("Не удалось сохранить сессию расклада") from exc

    async def delete(self, telegram_id: int) -> None:
        """Удаляет сессию (отмена расклада или после успешного сохранения)."""
        try:
            await self.redis.delete(self._key(telegram_id))
        except Exception as exc:
            raise ExternalServiceException("Не удалось удалить сессию расклада") from exc


class ReadingSessionStoreProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def reading_session_store(self, redis: Redis) -> ReadingSessionStore:
        return ReadingSessionStore(redis)
