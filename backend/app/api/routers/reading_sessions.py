from __future__ import annotations

from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from app.api.access_control import TELEGRAM_ID, VERIFY_INTERNAL_TOKEN
from app.api.schemas.common_dto import MessageDTO
from app.api.schemas.reading_session_dto import (
    DrawCardResultDTO,
    ReadingSessionDTO,
    StartSessionDTO,
)
from app.api.services.reading_session_service import ReadingSessionService

router = APIRouter(
    prefix="/readings/sessions",
    tags=["reading-sessions"],
    route_class=DishkaRoute,
    dependencies=[VERIFY_INTERNAL_TOKEN],
)


@router.post("", response_model=ReadingSessionDTO)
async def create_reading_session(
    body: StartSessionDTO,
    telegram_id: Annotated[int, TELEGRAM_ID],
    service: FromDishka[ReadingSessionService],
) -> ReadingSessionDTO:
    """
    Старт нового расклада (заменяет предыдущую активную сессию).

    Параметры:
    - **body** (StartSessionDTO): тип расклада и опциональный вопрос.
    - **X-Telegram-Id** (header): Telegram ID пользователя.
    - **X-Internal-Token** (header): токен бота.

    Возвращает:
    - **ReadingSessionDTO**: состояние новой сессии в Redis.
    """
    return await service.start_session(telegram_id, body)


@router.get("/current", response_model=ReadingSessionDTO)
async def get_current_reading_session(
    telegram_id: Annotated[int, TELEGRAM_ID],
    service: FromDishka[ReadingSessionService],
) -> ReadingSessionDTO:
    """
    Текущая активная сессия расклада.

    Параметры:
    - **X-Telegram-Id** (header): Telegram ID пользователя.
    - **X-Internal-Token** (header): токен бота.

    Возвращает:
    - **ReadingSessionDTO**: состояние сессии или 404.
    """
    return await service.get_current_session(telegram_id)


@router.delete("/current", response_model=MessageDTO)
async def delete_current_reading_session(
    telegram_id: Annotated[int, TELEGRAM_ID],
    service: FromDishka[ReadingSessionService],
) -> MessageDTO:
    """
    Отмена активного расклада (/cancel).

    Параметры:
    - **X-Telegram-Id** (header): Telegram ID пользователя.
    - **X-Internal-Token** (header): токен бота.

    Возвращает:
    - **MessageDTO**: подтверждение отмены.
    """
    await service.cancel_session(telegram_id)
    return MessageDTO(message="Расклад отменён")


@router.post("/draw", response_model=DrawCardResultDTO)
async def draw_reading_card(
    telegram_id: Annotated[int, TELEGRAM_ID],
    service: FromDishka[ReadingSessionService],
) -> DrawCardResultDTO:
    """
    Вытягивание следующей карты; на последней — LLM и сохранение в БД.

    Параметры:
    - **X-Telegram-Id** (header): Telegram ID пользователя.
    - **X-Internal-Token** (header): токен бота.

    Возвращает:
    - **DrawCardResultDTO**: выпавшая карта, обновлённая сессия, при завершении — reading.
    """
    return await service.draw_card(telegram_id)
