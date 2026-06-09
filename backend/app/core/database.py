"""Database session dependencies are provided by Dishka container in app.core.container."""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db_helper import db_helper


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Unit of Work для HTTP-запроса (транзакционный).
    """
    async with db_helper.session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_readonly_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Сессия только для чтения. Не выполняет commit.
    """
    async with db_helper.session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
