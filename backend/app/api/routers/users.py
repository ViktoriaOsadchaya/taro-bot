from __future__ import annotations

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from app.api.access_control import VERIFY_INTERNAL_TOKEN
from app.api.schemas.user_dto import UserReadDTO, UserUpsertDTO
from app.api.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
    route_class=DishkaRoute,
    dependencies=[VERIFY_INTERNAL_TOKEN],
)


@router.post("/upsert", response_model=UserReadDTO)
async def upsert_user(
    body: UserUpsertDTO,
    service: FromDishka[UserService],
) -> UserReadDTO:
    """
    Создание или обновление пользователя Telegram (вызывается на /start).

    Параметры:
    - **body** (UserUpsertDTO): telegram_id, username, first_name, language_code.
    - **X-Internal-Token** (header): токен бота.

    Возвращает:
    - **UserReadDTO**: сохранённый пользователь.
    """
    return await service.upsert(body)
