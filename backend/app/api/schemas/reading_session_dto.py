from pydantic import BaseModel, Field

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
