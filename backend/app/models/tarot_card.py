from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base
from app.models.enums import Arcana, Suit

if TYPE_CHECKING:
    from app.models.reading_card import ReadingCard


class TarotCard(Base):
    """
    Справочник одной карты колоды (всего 78 записей после seed-миграции).

    Данные статичны: пользователь не создаёт карты через API.
    Перевёрнутое положение не хранится здесь — только в ReadingCard.is_reversed.
    """

    # Стабильный машинный ключ, напр. major_00_fool, cups_ace — для seed и путей к файлам.
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name_ru: Mapped[str] = mapped_column(String(128), nullable=False)
    name_en: Mapped[str] = mapped_column(String(128), nullable=False)
    arcana: Mapped[Arcana] = mapped_column(Enum(Arcana, native_enum=False), nullable=False)
    # NULL для старших арканов.
    suit: Mapped[Suit | None] = mapped_column(Enum(Suit, native_enum=False), nullable=True)
    # 0–21 для major, 1–14 (туз–король) для minor.
    number: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    # Относительный путь к upright-изображению; reversed — поворот на клиенте.
    image_path: Mapped[str] = mapped_column(String(512), nullable=False)

    reading_cards: Mapped[list[ReadingCard]] = relationship(
        "ReadingCard",
        back_populates="tarot_card",
        lazy="selectin",
    )
