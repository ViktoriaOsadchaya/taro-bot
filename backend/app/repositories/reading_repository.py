from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.models.reading import Reading
from app.models.reading_card import ReadingCard
from app.repositories.base_repository import BaseRepository

_READING_WITH_CARDS = selectinload(Reading.cards).selectinload(ReadingCard.tarot_card)


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
        reading_id = reading.primary_key
        await session.flush()
        session.expire_all()
        return await self.get_with_cards(session, reading_id)

    async def get_with_cards(self, session: AsyncSession, reading_id: int) -> Reading:
        """Reading с cards и tarot_card — для DTO без lazy-load в async."""
        stmt = (
            select(Reading)
            .where(Reading.primary_key == reading_id)
            .options(_READING_WITH_CARDS)
        )
        result = await session.execute(stmt)
        reading = result.scalar_one_or_none()
        if reading is None:
            raise NotFoundException("Расклад не найден")
        return reading

    async def find_for_user_with_cards(
        self,
        session: AsyncSession,
        user_id: int,
        reading_id: int,
    ) -> Reading | None:
        """Reading пользователя с cards и tarot_card или None."""
        stmt = (
            select(Reading)
            .where(Reading.primary_key == reading_id, Reading.user_id == user_id)
            .options(_READING_WITH_CARDS)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


reading_repository = ReadingRepository()
