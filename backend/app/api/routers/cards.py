from __future__ import annotations

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends

from app.api.deps.bot_auth import verify_internal_token
from app.api.schemas.tarot_card_dto import TarotCardReadDTO
from app.api.services.tarot_card_service import TarotCardService

router = APIRouter(
    prefix="/cards",
    tags=["cards"],
    route_class=DishkaRoute,
    dependencies=[Depends(verify_internal_token)],
)


@router.get("", response_model=list[TarotCardReadDTO])
async def list_cards(
    service: FromDishka[TarotCardService],
) -> list[TarotCardReadDTO]:
    """
    Полный справочник карт колоды (78 карт).

    Параметры:
    - **X-Internal-Token** (header): токен бота.

    Возвращает:
    - **list[TarotCardReadDTO]**: все карты, отсортированные по code.
    """
    return await service.list_all()
