from dishka import Provider, Scope, provide
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tarot_card import TarotCard
from app.repositories.base_repository import BaseRepository


class TarotCardRepository(BaseRepository[TarotCard]):
    """
    Доступ к справочнику tarot_cards.

    Используется TarotCardService для случайного выбора карт
    и seed-миграций для первичного наполнения колоды.
    """

    def __init__(self) -> None:
        super().__init__(TarotCard)

    async def get_all_ordered(self, session: AsyncSession) -> list[TarotCard]:
        """Возвращает все 78 карт, отсортированные по code (стабильный порядок для UI)."""
        stmt = select(TarotCard).order_by(TarotCard.code)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_available_excluding(
        self,
        session: AsyncSession,
        exclude_ids: list[int],
    ) -> list[TarotCard]:
        """
        Возвращает карты, ещё не выпавшие в текущем раскладе.

        ***exclude_ids: primary_key карт, уже вытянутых в сессии Redis***
        """
        stmt = select(TarotCard).order_by(TarotCard.code)
        if exclude_ids:
            stmt = stmt.where(TarotCard.primary_key.not_in(exclude_ids))
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_code(self, session: AsyncSession, code: str) -> TarotCard | None:
        """Возвращает карту по стабильному коду (major_00_fool и т.п.)."""
        return await self.find_by_field(session, "code", code)


tarot_card_repository = TarotCardRepository()


class TarotCardRepoProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def tarot_card_repository(self) -> TarotCardRepository:
        return tarot_card_repository
