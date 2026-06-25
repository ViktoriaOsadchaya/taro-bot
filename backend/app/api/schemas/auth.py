from pydantic import BaseModel, Field

from app.api.schemas.user_dto import UserReadDTO


class AuthRequestDTO(BaseModel):
    """Запрос авторизации через Telegram WebApp initData."""

    init_data: str = Field(..., min_length=1, description="Строка Telegram.WebApp.initData")


class AuthResponseDTO(BaseModel):
    """Ответ после успешной авторизации."""

    access_token: str
    token_type: str = "bearer"
    user: UserReadDTO
