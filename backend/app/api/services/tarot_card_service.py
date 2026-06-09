import random

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.tarot_card_dto import TarotCardReadDTO
from app.core.exceptions import ValidationException
from app.models.tarot_card import TarotCard
from app.repositories.tarot_card_repository import TarotCardRepository


class TarotCardService:
    """
    Работа со справочником карт Таро.

    Отвечает за чтение колоды и случайный выбор карты без повторов.
    Используется ReadingSessionService при каждом нажатии «Вытянуть карту».
    """

    def __init__(self, session: AsyncSession, tarot_card_repo: TarotCardRepository) -> None:
        self.session = session
        self.tarot_card_repo = tarot_card_repo

    async def list_all(self) -> list[TarotCardReadDTO]:
        """Возвращает полную колоду (78 карт) для WebApp и админки."""
        cards = await self.tarot_card_repo.get_all_ordered(self.session)
        return [TarotCardReadDTO.model_validate(card) for card in cards]

    async def draw_random(
        self,
        exclude_ids: list[int],
    ) -> tuple[TarotCard, bool]:
        """
        Случайно выбирает карту из оставшихся и определяет перевёрнутость (~50%).

        ***exclude_ids: primary_key уже вытянутых карт в текущей сессии***

        Returns:
            Кортеж (TarotCard, is_reversed).
        """
        available = await self.tarot_card_repo.get_available_excluding(
            self.session,
            exclude_ids,
        )
        if not available:
            raise ValidationException("В колоде не осталось доступных карт")
        card = random.choice(available)
        is_reversed = random.random() < 0.5
        return card, is_reversed


class TarotCardServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def tarot_card_service(
        self,
        session: AsyncSession,
        tarot_card_repo: TarotCardRepository,
    ) -> TarotCardService:
        return TarotCardService(session, tarot_card_repo)
