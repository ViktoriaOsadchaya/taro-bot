from __future__ import annotations

from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Path, Query

from app.api.deps.auth_deps import CURRENT_USER
from app.api.schemas.reading_dto import ReadingDetailDTO, ReadingHistoryDTO
from app.api.schemas.user_dto import UserReadDTO
from app.api.services.reading_service import ReadingService

router = APIRouter(route_class=DishkaRoute)


@router.get("/", response_model=ReadingHistoryDTO)
async def list_readings(
    current_user: Annotated[UserReadDTO, CURRENT_USER],
    reading_service: FromDishka[ReadingService],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ReadingHistoryDTO:
    """
    История завершённых раскладов пользователя (/history).

    Параметры:
    - **Authorization** (header): Bearer JWT.
    - **skip** (int): пропуск записей.
    - **limit** (int): размер страницы (1–100).

    Возвращает:
    - **ReadingHistoryDTO**: пагинированный список раскладов.
    """
    return await reading_service.get_history(current_user.primary_key, skip=skip, limit=limit)


@router.post("/{reading_id}/regenerate", response_model=ReadingDetailDTO)
async def regenerate_reading(
    reading_id: Annotated[int, Path(ge=1)],
    current_user: Annotated[UserReadDTO, CURRENT_USER],
    reading_service: FromDishka[ReadingService],
) -> ReadingDetailDTO:
    """
    Перегенерация толкования расклада через LLM.

    Параметры:
    - **reading_id** (int): primary_key расклада.
    - **Authorization** (header): Bearer JWT.

    Возвращает:
    - **ReadingDetailDTO**: обновлённый расклад со статусом completed или failed.
    """
    return await reading_service.regenerate(current_user.primary_key, reading_id)


@router.get("/{reading_id}", response_model=ReadingDetailDTO)
async def get_reading(
    reading_id: Annotated[int, Path(ge=1)],
    current_user: Annotated[UserReadDTO, CURRENT_USER],
    reading_service: FromDishka[ReadingService],
) -> ReadingDetailDTO:
    """
    Детальный просмотр одного расклада.

    Параметры:
    - **reading_id** (int): primary_key расклада.
    - **Authorization** (header): Bearer JWT.

    Возвращает:
    - **ReadingDetailDTO**: карты, статус, толкование (может быть пустым при generating).
    """
    return await reading_service.get_detail(current_user.primary_key, reading_id)
