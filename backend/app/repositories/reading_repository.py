from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reading import Reading
from app.models.reading_card import ReadingCard
from app.repositories.base_repository import BaseRepository


class ReadingRepository(BaseRepository[Reading]):
    """
    Доступ к таблицам readings и связанным reading_cards.

    Используется ReadingService для истории /history и сохранения
    завершённого расклада после LLM.
    """

    def __init__(self) -> None:
        super().__init__(Reading)

    async def create_with_cards(
        self,
        session: AsyncSession,
        reading_kwargs: dict,
        cards_kwargs: list[dict],
    ) -> Reading:
        """
        Атомарно создаёт Reading и связанные ReadingCard в одной транзакции.

        ***cards_kwargs: список dict для ReadingCard (tarot_card_id, position_index, ...)***
        """
        reading = await self.create(session, **reading_kwargs)
        for card_data in cards_kwargs:
            card = ReadingCard(reading_id=reading.primary_key, **card_data)
            session.add(card)
        await session.flush()
        await session.refresh(reading, attribute_names=["cards"])
        return reading


reading_repository = ReadingRepository()
