from dishka import Provider, Scope, provide

from app.api.schemas.reading_dto import ReadingDetailDTO
from app.api.schemas.reading_session_dto import (
    DrawCardResultDTO,
    DrawnCardSessionDTO,
    ReadingSessionDTO,
    StartSessionDTO,
)
from app.api.schemas.user_dto import UserReadDTO
from app.api.services.interpretation_service import InterpretationService
from app.api.services.reading_service import ReadingService
from app.api.services.tarot_card_service import TarotCardService
from app.api.services.user_service import UserService
from app.core.exceptions import (
    ConflictException,
    ExternalServiceException,
    NotFoundException,
    ValidationException,
)
from app.domain.spread_config import get_position_key, get_spread_definition
from app.infrastructure.reading_session_store import ReadingSessionStore


# Максимальная длина вопроса для «Свободного вопроса».
MAX_QUESTION_LENGTH = 500


class ReadingSessionService:
    """
    Оркестрация пошагового расклада: Redis-сессия, вытягивание карт, LLM, сохранение.

    Центральный сервис сценария гадания. Используется роутерами sessions
    и Telegram-handlers бота (/start → выбор расклада → draw → результат).
    """

    def __init__(
        self,
        session_store: ReadingSessionStore,
        user_service: UserService,
        tarot_card_service: TarotCardService,
        reading_service: ReadingService,
        interpretation_service: InterpretationService,
    ) -> None:
        self.session_store = session_store
        self.user_service = user_service
        self.tarot_card_service = tarot_card_service
        self.reading_service = reading_service
        self.interpretation_service = interpretation_service

    async def start_session(
        self,
        telegram_id: int,
        data: StartSessionDTO,
    ) -> ReadingSessionDTO:
        """
        Начинает новый расклад: заменяет предыдущую Redis-сессию, если была.

        ***telegram_id: идентификатор из Telegram (не users.primary_key)***
        """
        definition = get_spread_definition(data.spread_type)
        question = self._validate_question(definition.requires_question, data.question)

        session = ReadingSessionDTO(
            spread_type=data.spread_type,
            question=question,
            required_cards=definition.cards_count,
            drawn_cards=[],
        )
        await self.session_store.save(telegram_id, session)
        return session

    async def get_current_session(self, telegram_id: int) -> ReadingSessionDTO:
        """Возвращает активную сессию или 404."""
        session = await self.session_store.get(telegram_id)
        if session is None:
            raise NotFoundException("Активный расклад не найден")
        return session

    async def cancel_session(self, telegram_id: int) -> None:
        """Отменяет текущий расклад (/cancel или «Назад»)."""
        session = await self.session_store.get(telegram_id)
        if session is None:
            raise NotFoundException("Активный расклад не найден")
        await self.session_store.delete(telegram_id)

    async def draw_card(self, telegram_id: int) -> DrawCardResultDTO:
        """
        Вытягивает следующую карту; при заполнении колоды — LLM и сохранение в БД.

        После успешного сохранения Redis-сессия удаляется.
        """
        session = await self.session_store.get(telegram_id)
        if session is None:
            raise NotFoundException("Активный расклад не найден")

        if len(session.drawn_cards) >= session.required_cards:
            raise ConflictException("Все карты уже вытянуты")

        exclude_ids = [card.tarot_card_id for card in session.drawn_cards]
        tarot_card, is_reversed = await self.tarot_card_service.draw_random(exclude_ids)
        position_index = len(session.drawn_cards)
        position_key = get_position_key(session.spread_type, position_index)

        drawn = DrawnCardSessionDTO(
            tarot_card_id=tarot_card.primary_key,
            position_index=position_index,
            position_key=position_key,
            is_reversed=is_reversed,
            code=tarot_card.code,
            name_ru=tarot_card.name_ru,
            image_path=tarot_card.image_path,
        )
        updated_cards = [*session.drawn_cards, drawn]
        updated_session = session.model_copy(update={"drawn_cards": updated_cards})
        is_complete = len(updated_cards) >= session.required_cards

        if not is_complete:
            await self.session_store.save(telegram_id, updated_session)
            return DrawCardResultDTO(
                session=updated_session,
                drawn_card=drawn,
                is_complete=False,
            )

        # Последняя карта — финализация: LLM → PostgreSQL → очистка Redis.
        user = await self.user_service.get_by_telegram_id(telegram_id)
        reading_detail = await self._finalize_reading(user, updated_session)
        await self.session_store.delete(telegram_id)

        return DrawCardResultDTO(
            session=updated_session,
            drawn_card=drawn,
            is_complete=True,
            reading=reading_detail,
        )

    async def _finalize_reading(
        self,
        user: UserReadDTO,
        session: ReadingSessionDTO,
    ) -> ReadingDetailDTO:
        """Вызывает LLM и сохраняет расклад; при ошибке LLM — status=failed."""
        try:
            interpretation = await self.interpretation_service.generate(
                spread_type=session.spread_type,
                question=session.question,
                drawn_cards=session.drawn_cards,
            )
            return await self.reading_service.save_completed(
                user_id=user.primary_key,
                spread_type=session.spread_type,
                question=session.question,
                drawn_cards=session.drawn_cards,
                interpretation=interpretation,
            )
        except ExternalServiceException:
            await self.reading_service.save_failed(
                user_id=user.primary_key,
                spread_type=session.spread_type,
                question=session.question,
                drawn_cards=session.drawn_cards,
            )
            raise

    def _validate_question(self, requires_question: bool, question: str | None) -> str | None:
        """Проверяет обязательность и длину вопроса для FREE_QUESTION."""
        if not requires_question:
            if question is not None and question.strip():
                raise ValidationException("Для этого расклада вопрос не требуется")
            return None
        if question is None or not question.strip():
            raise ValidationException("Для этого расклада необходимо задать вопрос")
        cleaned = question.strip()
        if len(cleaned) > MAX_QUESTION_LENGTH:
            raise ValidationException(
                f"Вопрос не должен превышать {MAX_QUESTION_LENGTH} символов"
            )
        return cleaned


class ReadingSessionServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def reading_session_service(
        self,
        session_store: ReadingSessionStore,
        user_service: UserService,
        tarot_card_service: TarotCardService,
        reading_service: ReadingService,
        interpretation_service: InterpretationService,
    ) -> ReadingSessionService:
        return ReadingSessionService(
            session_store,
            user_service,
            tarot_card_service,
            reading_service,
            interpretation_service,
        )
