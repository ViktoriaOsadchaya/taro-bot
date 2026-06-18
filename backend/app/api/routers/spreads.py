from __future__ import annotations

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from app.api.access_control import VERIFY_INTERNAL_TOKEN
from app.api.schemas.spread_dto import SpreadTypeReadDTO
from app.api.services.spread_service import SpreadService

router = APIRouter(
    route_class=DishkaRoute,
    dependencies=[VERIFY_INTERNAL_TOKEN],
)


@router.get("/types", response_model=list[SpreadTypeReadDTO])
async def list_spread_types(
    service: FromDishka[SpreadService],
) -> list[SpreadTypeReadDTO]:
    """
    Список доступных типов раскладов для меню бота.

    Параметры:
    - **X-Internal-Token** (header): токен бота.

    Возвращает:
    - **list[SpreadTypeReadDTO]**: типы раскладов с описаниями.
    """
    return await service.list_spread_types()
