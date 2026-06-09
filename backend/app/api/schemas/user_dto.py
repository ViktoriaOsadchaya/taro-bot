from pydantic import BaseModel, Field


class UserUpsertDTO(BaseModel):
    """Входные данные профиля Telegram-пользователя."""

    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    language_code: str = "ru"


class UserReadDTO(BaseModel):
    """Публичное представление пользователя."""

    primary_key: int
    telegram_id: int
    username: str | None
    first_name: str | None
    language_code: str

    model_config = {"from_attributes": True}
