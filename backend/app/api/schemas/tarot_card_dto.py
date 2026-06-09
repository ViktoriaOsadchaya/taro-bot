from pydantic import BaseModel

from app.models.enums import Arcana, Suit


class TarotCardReadDTO(BaseModel):
    """Карта из справочника для UI и API."""

    primary_key: int
    code: str
    name_ru: str
    name_en: str
    arcana: Arcana
    suit: Suit | None
    number: int | None
    image_path: str

    model_config = {"from_attributes": True}
