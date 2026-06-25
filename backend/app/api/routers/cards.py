from __future__ import annotations

from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query

from app.api.schemas.tarot_card_dto import TarotCardReadDTO
from app.api.services.tarot_card_service import TarotCardService

router = APIRouter(route_class=DishkaRoute)


@router.get("/", response_model=list[TarotCardReadDTO])
async def list_cards(
    service: FromDishka[TarotCardService],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 78,
) -> list[TarotCardReadDTO]:
    """
    Справочник карт колоды (78 карт).

    Параметры:
    - **Authorization** (header): Bearer JWT.
    - **skip** (int): пропуск записей.
    - **limit** (int): размер страницы (1–100).

    Возвращает:
    - **list[TarotCardReadDTO]**: карты, отсортированные по code.
    """
    return await service.list_all(skip=skip, limit=limit)
