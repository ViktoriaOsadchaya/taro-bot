from __future__ import annotations

from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from app.api.deps.auth_deps import CURRENT_USER
from app.api.schemas.user_dto import UserReadDTO, UserUpsertDTO
from app.api.services.user_service import UserService

router = APIRouter(route_class=DishkaRoute)


@router.get("/me", response_model=UserReadDTO)
async def get_current_user_profile(
    current_user: Annotated[UserReadDTO, CURRENT_USER],
    user_service: FromDishka[UserService],
) -> UserReadDTO:
    """
    Текущий авторизованный пользователь.

    Параметры:
    - **Authorization** (header): Bearer JWT.

    Возвращает:
    - **UserReadDTO**: актуальный профиль из БД.
    """
    return await user_service.get_by_telegram_id(current_user.telegram_id)


@router.post("/upsert", response_model=UserReadDTO)
async def upsert_user(
    body: UserUpsertDTO,
    service: FromDishka[UserService],
) -> UserReadDTO:
    """
    Создание или обновление пользователя Telegram.

    Параметры:
    - **body** (UserUpsertDTO): telegram_id, username, first_name, language_code.
    - **Authorization** (header): Bearer JWT.

    Возвращает:
    - **UserReadDTO**: сохранённый пользователь.
    """
    return await service.upsert(body)
