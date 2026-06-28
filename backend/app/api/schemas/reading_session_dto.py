from pydantic import BaseModel, Field, model_validator

from app.api.schemas.reading_dto import ReadingDetailDTO
from app.models.enums import CardPositionKey, SpreadType


class DrawnCardSessionDTO(BaseModel):
    """Карта, уже вытянутая в активной Redis-сессии."""

    tarot_card_id: int
    position_index: int
    position_key: CardPositionKey
    is_reversed: bool
    code: str
    name_ru: str
    image_path: str

    @model_validator(mode="before")
    @classmethod
    def from_reading_card_orm(cls, data: object) -> object:
        if hasattr(data, "tarot_card_id") and hasattr(data, "tarot_card"):
            tarot = data.tarot_card
            return {
                "tarot_card_id": data.tarot_card_id,
                "position_index": data.position_index,
                "position_key": data.position_key,
                "is_reversed": data.is_reversed,
                "code": tarot.code,
                "name_ru": tarot.name_ru,
                "image_path": tarot.image_path,
            }
        return data


class ReadingSessionDTO(BaseModel):
    """Состояние незавершённого расклада в Redis."""

    spread_type: SpreadType
    question: str | None = None
    required_cards: int
    drawn_cards: list[DrawnCardSessionDTO] = Field(default_factory=list)


class StartSessionDTO(BaseModel):
    """Запрос на старт новой сессии расклада."""

    spread_type: SpreadType
    question: str | None = None


class DrawCardResultDTO(BaseModel):
    """Результат одного вытягивания карты."""

    session: ReadingSessionDTO
    drawn_card: DrawnCardSessionDTO
    is_complete: bool
    # Заполняется только когда is_complete=True и LLM успешно отработал.
    reading: ReadingDetailDTO | None = None
