"""Pydantic DTO общего назначения."""

from pydantic import BaseModel


class MessageDTO(BaseModel):
    """Простой текстовый ответ (удаление, отмена и т.п.)."""

    message: str


class HealthDTO(BaseModel):
    """Ответ liveness-probe."""

    status: str
