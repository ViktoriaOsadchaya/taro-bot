from __future__ import annotations

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from app.api.schemas.common_dto import HealthDTO

# Публичный endpoint — без X-Internal-Token.
router = APIRouter(prefix="/health", tags=["system"], route_class=DishkaRoute)


@router.get("", response_model=HealthDTO)
async def get_health() -> HealthDTO:
    """
    Проверка доступности API (liveness).

    Параметры:
    - нет

    Возвращает:
    - **HealthDTO**: статус сервиса.
    """
    return HealthDTO(status="ok")
