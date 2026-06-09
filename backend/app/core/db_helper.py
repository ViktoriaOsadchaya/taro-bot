"""
Подключение к PostgreSQL через SQLAlchemy async engine.

Единая точка создания engine и session_factory для Dishka и Alembic.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


class DatabaseHelper:
    """Обёртка над async engine и фабрикой сессий."""

    def __init__(self, url: str, echo: bool = False) -> None:
        self.engine = create_async_engine(url, echo=echo, pool_pre_ping=True)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        """Закрывает пул соединений при остановке приложения."""
        await self.engine.dispose()


db_helper = DatabaseHelper(url=settings.db.url, echo=settings.db.echo)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Транзакционная сессия на один HTTP-запрос: commit при успехе, rollback при ошибке.
    """
    async with db_helper.session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
