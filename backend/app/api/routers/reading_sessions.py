from __future__ import annotations

from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from app.api.deps.auth_deps import CURRENT_USER
from app.api.schemas.common_dto import MessageDTO
from app.api.schemas.reading_session_dto import (
    DrawCardResultDTO,
    ReadingSessionDTO,
    StartSessionDTO,
)
from app.api.schemas.user_dto import UserReadDTO
from app.api.services.reading_session_service import ReadingSessionService

router = APIRouter(route_class=DishkaRoute)


@router.post("/", response_model=ReadingSessionDTO)
async def create_reading_session(
    body: StartSessionDTO,
    current_user: Annotated[UserReadDTO, CURRENT_USER],
    service: FromDishka[ReadingSessionService],
) -> ReadingSessionDTO:
    """
    Старт нового расклада (заменяет предыдущую активную сессию).

    Параметры:
    - **body** (StartSessionDTO): тип расклада и опциональный вопрос.
    - **Authorization** (header): Bearer JWT.

    Возвращает:
    - **ReadingSessionDTO**: состояние новой сессии в Redis.
    """
    return await service.start_session(current_user.telegram_id, body)


@router.get("/current", response_model=ReadingSessionDTO)
async def get_current_reading_session(
    current_user: Annotated[UserReadDTO, CURRENT_USER],
    service: FromDishka[ReadingSessionService],
) -> ReadingSessionDTO:
    """
    Текущая активная сессия расклада.

    Параметры:
    - **Authorization** (header): Bearer JWT.

    Возвращает:
    - **ReadingSessionDTO**: состояние сессии или 404.
    """
    return await service.get_current_session(current_user.telegram_id)


@router.delete("/current", response_model=MessageDTO)
async def delete_current_reading_session(
    current_user: Annotated[UserReadDTO, CURRENT_USER],
    service: FromDishka[ReadingSessionService],
) -> MessageDTO:
    """
    Отмена активного расклада (/cancel).

    Параметры:
    - **Authorization** (header): Bearer JWT.

    Возвращает:
    - **MessageDTO**: подтверждение отмены.
    """
    await service.cancel_session(current_user.telegram_id)
    return MessageDTO(message="Расклад отменён")


@router.post("/draw", response_model=DrawCardResultDTO)
async def draw_reading_card(
    current_user: Annotated[UserReadDTO, CURRENT_USER],
    service: FromDishka[ReadingSessionService],
) -> DrawCardResultDTO:
    """
    Вытягивание следующей карты; на последней — LLM и сохранение в БД.

    Параметры:
    - **Authorization** (header): Bearer JWT.

    Возвращает:
    - **DrawCardResultDTO**: выпавшая карта, обновлённая сессия, при завершении — reading.
    """
    return await service.draw_card(current_user.telegram_id)
