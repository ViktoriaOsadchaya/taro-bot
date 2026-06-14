from __future__ import annotations

from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Path, Query

from app.api.access_control import TELEGRAM_ID, VERIFY_INTERNAL_TOKEN
from app.api.schemas.reading_dto import ReadingDetailDTO, ReadingHistoryDTO
from app.api.services.reading_service import ReadingService
from app.api.services.user_service import UserService

router = APIRouter(
    prefix="/readings",
    tags=["readings"],
    route_class=DishkaRoute,
    dependencies=[VERIFY_INTERNAL_TOKEN],
)


@router.get("", response_model=ReadingHistoryDTO)
async def list_readings(
    telegram_id: Annotated[int, TELEGRAM_ID],
    user_service: FromDishka[UserService],
    reading_service: FromDishka[ReadingService],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ReadingHistoryDTO:
    """
    История завершённых раскладов пользователя (/history).

    Параметры:
    - **X-Telegram-Id** (header): Telegram ID пользователя.
    - **X-Internal-Token** (header): токен бота.
    - **skip** (int): пропуск записей.
    - **limit** (int): размер страницы (1–100).

    Возвращает:
    - **ReadingHistoryDTO**: пагинированный список раскладов.
    """
    user = await user_service.get_by_telegram_id(telegram_id)
    return await reading_service.get_history(user.primary_key, skip=skip, limit=limit)


@router.get("/{reading_id}", response_model=ReadingDetailDTO)
async def get_reading(
    reading_id: Annotated[int, Path(ge=1)],
    telegram_id: Annotated[int, TELEGRAM_ID],
    user_service: FromDishka[UserService],
    reading_service: FromDishka[ReadingService],
) -> ReadingDetailDTO:
    """
    Детальный просмотр одного расклада.

    Параметры:
    - **reading_id** (int): primary_key расклада.
    - **X-Telegram-Id** (header): Telegram ID пользователя.
    - **X-Internal-Token** (header): токен бота.

    Возвращает:
    - **ReadingDetailDTO**: карты, толкование, метаданные.
    """
    user = await user_service.get_by_telegram_id(telegram_id)
    return await reading_service.get_detail(user.primary_key, reading_id)
