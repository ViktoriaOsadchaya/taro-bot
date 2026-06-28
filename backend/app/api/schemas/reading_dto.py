from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel, Field, model_validator

from app.domain.spread_config import POSITION_LABELS_RU
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

    @model_validator(mode="before")
    @classmethod
    def from_reading_card_orm(cls, data: object) -> object:
        if hasattr(data, "tarot_card_id") and hasattr(data, "tarot_card"):
            tarot = data.tarot_card
            return {
                "tarot_card_id": data.tarot_card_id,
                "code": tarot.code,
                "name_ru": tarot.name_ru,
                "image_path": tarot.image_path,
                "position_index": data.position_index,
                "position_key": data.position_key,
                "position_label_ru": POSITION_LABELS_RU.get(
                    data.position_key,
                    data.position_key.value,
                ),
                "is_reversed": data.is_reversed,
            }
        return data


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

    @model_validator(mode="before")
    @classmethod
    def from_reading_orm(cls, data: object) -> object:
        if hasattr(data, "primary_key") and hasattr(data, "cards"):
            return {
                "primary_key": data.primary_key,
                "spread_type": data.spread_type,
                "question": data.question,
                "interpretation": data.interpretation,
                "status": data.status,
                "llm_model": data.llm_model,
                "completed_at": data.completed_at,
                "created_at": data.created_at,
                "cards": [ReadingCardReadDTO.model_validate(rc) for rc in data.cards],
            }
        return data


class ReadingHistoryItemDTO(BaseModel):
    """Краткая запись для списка /history."""

    INTERPRETATION_PREVIEW_LENGTH: ClassVar[int] = 120

    primary_key: int
    spread_type: SpreadType
    question: str | None
    interpretation_preview: str
    created_at: datetime
    cards_count: int

    @model_validator(mode="before")
    @classmethod
    def from_reading_orm(cls, data: object) -> object:
        if hasattr(data, "primary_key") and hasattr(data, "cards"):
            preview = data.interpretation or ""
            if len(preview) > cls.INTERPRETATION_PREVIEW_LENGTH:
                preview = preview[: cls.INTERPRETATION_PREVIEW_LENGTH].rstrip() + "…"
            return {
                "primary_key": data.primary_key,
                "spread_type": data.spread_type,
                "question": data.question,
                "interpretation_preview": preview,
                "created_at": data.created_at,
                "cards_count": len(data.cards),
            }
        return data


class ReadingHistoryDTO(BaseModel):
    """Пагинированная история раскладов."""

    items: list[ReadingHistoryItemDTO]
    total: int
    skip: int
    limit: int
