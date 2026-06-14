from datetime import UTC, datetime

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.reading_dto import (
    ReadingCardReadDTO,
    ReadingDetailDTO,
    ReadingHistoryDTO,
    ReadingHistoryItemDTO,
)
from app.api.schemas.reading_session_dto import DrawnCardSessionDTO
from app.core.config import settings
from app.core.exceptions import NotFoundException
from app.domain.spread_config import POSITION_LABELS_RU
from app.models.enums import ReadingStatus, SpreadType
from app.repositories.reading_repository import ReadingRepository


class ReadingService:
    """
    Сохранение и чтение завершённых раскладов в PostgreSQL.

    Обслуживает /history и детальный просмотр расклада.
    Вызывается ReadingSessionService после успешного ответа LLM.
    """

    INTERPRETATION_PREVIEW_LENGTH = 120

    def __init__(self, session: AsyncSession, reading_repo: ReadingRepository) -> None:
        self.session = session
        self.reading_repo = reading_repo

    async def get_history(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> ReadingHistoryDTO:
        """Возвращает пагинированную историю завершённых раскладов пользователя."""
        readings, total = await self.reading_repo.get_paginated(
            self.session,
            skip=skip,
            limit=limit,
            order_by="created_at",
            order_desc=True,
            filters={"user_id": user_id, "status": ReadingStatus.COMPLETED},
            relations=["cards"],
        )
        items = [self._to_history_item(reading) for reading in readings]
        return ReadingHistoryDTO(items=items, total=total, skip=skip, limit=limit)

    async def get_detail(self, user_id: int, reading_id: int) -> ReadingDetailDTO:
        """Возвращает полный расклад, если он принадлежит пользователю."""
        reading = await self.reading_repo.find_by_conditions(
            self.session,
            {"primary_key": reading_id, "user_id": user_id},
        )
        if reading is None:
            raise NotFoundException("Расклад не найден")
        return self._to_detail(reading)

    async def save_completed(
        self,
        user_id: int,
        spread_type: SpreadType,
        question: str | None,
        drawn_cards: list[DrawnCardSessionDTO],
        interpretation: str,
    ) -> ReadingDetailDTO:
        """
        Сохраняет успешный расклад с картами и текстом толкования.

        ***drawn_cards: финальный список из Redis-сессии***
        """
        reading = await self.reading_repo.create_with_cards(
            self.session,
            reading_kwargs={
                "user_id": user_id,
                "spread_type": spread_type,
                "question": question,
                "interpretation": interpretation,
                "status": ReadingStatus.COMPLETED,
                "llm_model": settings.llm.model,
                "completed_at": datetime.now(UTC),
            },
            cards_kwargs=self._cards_kwargs(drawn_cards),
        )
        return self._to_detail(reading)

    async def save_failed(
        self,
        user_id: int,
        spread_type: SpreadType,
        question: str | None,
        drawn_cards: list[DrawnCardSessionDTO],
    ) -> None:
        """Сохраняет неудачный расклад без толкования (не попадает в /history)."""
        await self.reading_repo.create_with_cards(
            self.session,
            reading_kwargs={
                "user_id": user_id,
                "spread_type": spread_type,
                "question": question,
                "interpretation": None,
                "status": ReadingStatus.FAILED,
                "llm_model": settings.llm.model,
                "completed_at": datetime.now(UTC),
            },
            cards_kwargs=self._cards_kwargs(drawn_cards),
        )

    def _cards_kwargs(self, drawn_cards: list[DrawnCardSessionDTO]) -> list[dict]:
        """Преобразует карты сессии в kwargs для ReadingCard."""
        return [
            {
                "tarot_card_id": card.tarot_card_id,
                "position_index": card.position_index,
                "position_key": card.position_key,
                "is_reversed": card.is_reversed,
            }
            for card in drawn_cards
        ]

    def _to_history_item(self, reading) -> ReadingHistoryItemDTO:
        """Преобразует ORM Reading в краткую запись истории."""
        preview = reading.interpretation or ""
        if len(preview) > self.INTERPRETATION_PREVIEW_LENGTH:
            preview = preview[: self.INTERPRETATION_PREVIEW_LENGTH].rstrip() + "…"
        return ReadingHistoryItemDTO(
            primary_key=reading.primary_key,
            spread_type=reading.spread_type,
            question=reading.question,
            interpretation_preview=preview,
            created_at=reading.created_at,
            cards_count=len(reading.cards),
        )

    def _to_detail(self, reading) -> ReadingDetailDTO:
        """Преобразует ORM Reading с cards в полный DTO."""
        cards = []
        for rc in reading.cards:
            tarot = rc.tarot_card
            cards.append(
                ReadingCardReadDTO(
                    tarot_card_id=rc.tarot_card_id,
                    code=tarot.code,
                    name_ru=tarot.name_ru,
                    image_path=tarot.image_path,
                    position_index=rc.position_index,
                    position_key=rc.position_key,
                    position_label_ru=POSITION_LABELS_RU.get(
                        rc.position_key,
                        rc.position_key.value,
                    ),
                    is_reversed=rc.is_reversed,
                )
            )
        return ReadingDetailDTO(
            primary_key=reading.primary_key,
            spread_type=reading.spread_type,
            question=reading.question,
            interpretation=reading.interpretation,
            status=reading.status,
            llm_model=reading.llm_model,
            completed_at=reading.completed_at,
            created_at=reading.created_at,
            cards=cards,
        )


class ReadingServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def reading_service(
        self,
        session: AsyncSession,
        reading_repo: ReadingRepository,
    ) -> ReadingService:
        return ReadingService(session, reading_repo)
