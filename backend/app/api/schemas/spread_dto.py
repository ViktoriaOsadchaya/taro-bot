from pydantic import BaseModel

from app.models.enums import SpreadType


class SpreadTypeReadDTO(BaseModel):
    """Описание типа расклада для меню бота и GET /spreads/types."""

    spread_type: SpreadType
    cards_count: int
    requires_question: bool
    title_ru: str
    description_ru: str
