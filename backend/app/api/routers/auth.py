from __future__ import annotations

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from app.api.auth.jwt_utils import create_access_token
from app.api.auth.telegram_validator import validate_init_data
from app.api.schemas.auth import AuthRequestDTO, AuthResponseDTO
from app.api.schemas.user_dto import UserUpsertDTO
from app.api.services.user_service import UserService

router = APIRouter(
    tags=["auth"],
    route_class=DishkaRoute,
)


@router.post("/telegram", response_model=AuthResponseDTO)
async def auth_telegram(
    body: AuthRequestDTO,
    user_service: FromDishka[UserService],
) -> AuthResponseDTO:
    """
    Авторизация через Telegram WebApp initData.

    Параметры:
    - **body.init_data**: строка `window.Telegram.WebApp.initData`.

    Возвращает:
    - **AuthResponseDTO**: JWT access_token и профиль пользователя.
    """
    telegram_user = validate_init_data(body.init_data)
    user = await user_service.upsert(
        UserUpsertDTO(
            telegram_id=telegram_user.telegram_id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            language_code=telegram_user.language_code,
        )
    )
    access_token = create_access_token(user)
    return AuthResponseDTO(access_token=access_token, user=user)
