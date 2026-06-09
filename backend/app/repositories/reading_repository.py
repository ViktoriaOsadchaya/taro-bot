from dishka import Provider, Scope, provide
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.models.enums import ReadingStatus
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

    async def get_by_id_with_cards(
        self,
        session: AsyncSession,
        reading_id: int,
        *,
        raise_if_not_found: bool = True,
    ) -> Reading | None:
        """Загружает расклад с картами и справочником TarotCard (eager selectinload)."""
        stmt = (
            select(Reading)
            .where(Reading.primary_key == reading_id)
            .options(
                selectinload(Reading.cards).selectinload(ReadingCard.tarot_card),
            )
        )
        result = await session.execute(stmt)
        reading = result.scalar_one_or_none()
        if reading is None and raise_if_not_found:
            raise NotFoundException("Расклад не найден")
        return reading

    async def get_by_id_for_user(
        self,
        session: AsyncSession,
        reading_id: int,
        user_id: int,
    ) -> Reading | None:
        """Возвращает расклад только если он принадлежит указанному user_id."""
        stmt = (
            select(Reading)
            .where(
                Reading.primary_key == reading_id,
                Reading.user_id == user_id,
            )
            .options(
                selectinload(Reading.cards).selectinload(ReadingCard.tarot_card),
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_completed_by_user_paginated(
        self,
        session: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Reading], int]:
        """
        История раскладов пользователя: только COMPLETED, новые сверху.

        ***user_id: users.primary_key (не telegram_id)***
        """
        base_filter = (
            Reading.user_id == user_id,
            Reading.status == ReadingStatus.COMPLETED,
        )

        count_stmt = select(func.count()).select_from(Reading).where(*base_filter)
        total = (await session.execute(count_stmt)).scalar_one()

        stmt = (
            select(Reading)
            .where(*base_filter)
            .order_by(Reading.created_at.desc())
            .offset(skip)
            .limit(limit)
            .options(
                selectinload(Reading.cards).selectinload(ReadingCard.tarot_card),
            )
        )
        result = await session.execute(stmt)
        return list(result.scalars().all()), total

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


class ReadingRepoProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def reading_repository(self) -> ReadingRepository:
        return reading_repository
