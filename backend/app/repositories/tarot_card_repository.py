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


tarot_card_repository = TarotCardRepository()
