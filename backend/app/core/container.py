"""
DI-контейнер Dishka: регистрация сессии БД и репозиториев.

Новые Provider'ы добавлять в ALL_PROVIDERS и документировать в core/README.md.
"""

from collections.abc import AsyncIterable

from dishka import Provider, Scope, make_async_container, provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.services.interpretation_service import InterpretationServiceProvider
from app.api.services.reading_service import ReadingServiceProvider
from app.api.services.reading_session_service import ReadingSessionServiceProvider
from app.api.services.spread_service import SpreadServiceProvider
from app.api.services.tarot_card_service import TarotCardServiceProvider
from app.api.services.user_service import UserServiceProvider
from app.core.db_helper import db_helper
from app.core.redis_helper import redis_helper
from app.infrastructure.llm_client import LlmClientProvider
from app.infrastructure.reading_session_store import ReadingSessionStoreProvider
from app.repositories.reading_repository import ReadingRepoProvider
from app.repositories.tarot_card_repository import TarotCardRepoProvider
from app.repositories.user_repository import UserRepoProvider


class DbProvider(Provider):
    """Предоставляет транзакционную AsyncSession на scope одного запроса."""

    scope = Scope.REQUEST

    @provide
    async def session(self) -> AsyncIterable[AsyncSession]:
        """
        Открывает сессию на время обработки запроса.
        Commit при успешном завершении, rollback при любом исключении.
        """
        async with db_helper.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


class RedisProvider(Provider):
    """Предоставляет клиент Redis (APP scope — одно подключение на процесс)."""

    scope = Scope.APP

    @provide
    def redis(self) -> Redis:
        return redis_helper.client


ALL_PROVIDERS: list[Provider] = [
    DbProvider(),
    RedisProvider(),
    UserRepoProvider(),
    TarotCardRepoProvider(),
    ReadingRepoProvider(),
    ReadingSessionStoreProvider(),
    LlmClientProvider(),
    UserServiceProvider(),
    SpreadServiceProvider(),
    TarotCardServiceProvider(),
    ReadingServiceProvider(),
    InterpretationServiceProvider(),
    ReadingSessionServiceProvider(),
]

container = make_async_container(*ALL_PROVIDERS)
