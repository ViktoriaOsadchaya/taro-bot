from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import CardPositionKey, ReadingStatus, SpreadType


class ReadingCardReadDTO(BaseModel):
    """Карта в сохранённом раскладе."""

    tarot_card_id: int
    code: str
    name_ru: str
    image_path: str
    position_index: int
    position_key: CardPositionKey
    position_label_ru: str
    is_reversed: bool


class ReadingDetailDTO(BaseModel):
    """Полный расклад с толкованием."""

    primary_key: int
    spread_type: SpreadType
    question: str | None
    interpretation: str | None
    status: ReadingStatus
    llm_model: str | None
    completed_at: datetime | None
    created_at: datetime
    cards: list[ReadingCardReadDTO]


class ReadingHistoryItemDTO(BaseModel):
    """Краткая запись для списка /history."""

    primary_key: int
    spread_type: SpreadType
    question: str | None
    interpretation_preview: str
    created_at: datetime
    cards_count: int


class ReadingHistoryDTO(BaseModel):
    """Пагинированная история раскладов."""

    items: list[ReadingHistoryItemDTO]
    total: int
    skip: int
    limit: int
