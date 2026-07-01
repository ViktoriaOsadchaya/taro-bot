from datetime import UTC, datetime

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.reading_dto import (
    ReadingDetailDTO,
    ReadingHistoryDTO,
    ReadingHistoryItemDTO,
)
from app.api.schemas.reading_session_dto import DrawnCardSessionDTO
from app.api.services.interpretation_service import InterpretationService
from app.core.config import settings
from app.core.exceptions import ConflictException, ExternalServiceException, NotFoundException
from app.models.enums import ReadingStatus, SpreadType
from app.repositories.reading_repository import ReadingRepository


class ReadingService:
    """
    Сохранение и чтение завершённых раскладов в PostgreSQL.

    Обслуживает /history и детальный просмотр расклада.
    Вызывается ReadingSessionService после успешного ответа LLM.
    """

    def __init__(
        self,
        session: AsyncSession,
        reading_repo: ReadingRepository,
        interpretation_service: InterpretationService,
    ) -> None:
        self.session = session
        self.reading_repo = reading_repo
        self.interpretation_service = interpretation_service

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
        items = [ReadingHistoryItemDTO.model_validate(reading) for reading in readings]
        return ReadingHistoryDTO.model_validate(
            {"items": items, "total": total, "skip": skip, "limit": limit}
        )

    async def get_detail(self, user_id: int, reading_id: int) -> ReadingDetailDTO:
        """Возвращает полный расклад, если он принадлежит пользователю."""
        reading = await self._get_reading_for_user(user_id, reading_id)
        return ReadingDetailDTO.model_validate(reading)

    async def save_generating(
        self,
        user_id: int,
        spread_type: SpreadType,
        question: str | None,
        drawn_cards: list[DrawnCardSessionDTO],
    ) -> ReadingDetailDTO:
        """
        Сохраняет расклад со статусом GENERATING до ответа LLM.

        ***drawn_cards: финальный список из Redis-сессии***
        """
        reading = await self.reading_repo.create_with_cards(
            self.session,
            reading_kwargs={
                "user_id": user_id,
                "spread_type": spread_type,
                "question": question,
                "interpretation": None,
                "status": ReadingStatus.GENERATING,
                "llm_model": settings.llm.model,
                "completed_at": None,
            },
            cards_kwargs=self._cards_kwargs(drawn_cards),
        )
        return ReadingDetailDTO.model_validate(reading)

    async def complete_reading(
        self,
        user_id: int,
        reading_id: int,
        interpretation: str,
    ) -> ReadingDetailDTO:
        """Обновляет расклад после успешной генерации LLM."""
        reading = await self._get_reading_for_user(user_id, reading_id)
        updated = await self.reading_repo.update(
            self.session,
            reading.primary_key,
            interpretation=interpretation,
            status=ReadingStatus.COMPLETED,
            llm_model=settings.llm.model,
            completed_at=datetime.now(UTC),
        )
        if updated is None:
            raise NotFoundException("Расклад не найден")
        reading = await self._get_reading_for_user(user_id, reading_id)
        return ReadingDetailDTO.model_validate(reading)

    async def mark_failed(self, user_id: int, reading_id: int) -> None:
        """Помечает существующий расклад как failed."""
        reading = await self._get_reading_for_user(user_id, reading_id)
        await self.reading_repo.update(
            self.session,
            reading.primary_key,
            interpretation=None,
            status=ReadingStatus.FAILED,
            completed_at=datetime.now(UTC),
        )

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
        return ReadingDetailDTO.model_validate(reading)

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

    async def regenerate(self, user_id: int, reading_id: int) -> ReadingDetailDTO:
        """Перегенерирует толкование расклада через LLM."""
        reading = await self._get_reading_for_user(user_id, reading_id)
        if reading.status == ReadingStatus.GENERATING:
            raise ConflictException("Расклад уже генерируется")

        drawn_cards = self._cards_to_session_dto(reading)
        await self.reading_repo.update(
            self.session,
            reading.primary_key,
            interpretation=None,
            status=ReadingStatus.GENERATING,
            completed_at=None,
        )

        try:
            interpretation = await self.interpretation_service.generate(
                spread_type=reading.spread_type,
                question=reading.question,
                drawn_cards=drawn_cards,
            )
            return await self.complete_reading(user_id, reading_id, interpretation)
        except ExternalServiceException:
            await self.mark_failed(user_id, reading_id)
            raise

    async def _get_reading_for_user(self, user_id: int, reading_id: int):
        """Возвращает ORM Reading пользователя или 404."""
        reading = await self.reading_repo.find_for_user_with_cards(
            self.session,
            user_id,
            reading_id,
        )
        if reading is None:
            raise NotFoundException("Расклад не найден")
        return reading

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

    def _cards_to_session_dto(self, reading) -> list[DrawnCardSessionDTO]:
        """Преобразует сохранённые карты расклада в DTO для LLM."""
        return [DrawnCardSessionDTO.model_validate(rc) for rc in reading.cards]


class ReadingServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def reading_service(
        self,
        session: AsyncSession,
        reading_repo: ReadingRepository,
        interpretation_service: InterpretationService,
    ) -> ReadingService:
        return ReadingService(session, reading_repo, interpretation_service)
