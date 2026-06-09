from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, SmallInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base
from app.models.enums import CardPositionKey

if TYPE_CHECKING:
    from app.models.reading import Reading
    from app.models.tarot_card import TarotCard


class ReadingCard(Base):
    """
    Связь «расклад ↔ карта» с контекстом позиции и ориентации.

    position_index — порядок вытягивания (0, 1, 2).
    position_key — смысл позиции для LLM (past, day, insight_1 и т.д.).
    """

    __table_args__ = (
        # В одном раскладе не может быть двух карт с одинаковым порядковым номером.
        UniqueConstraint("reading_id", "position_index", name="uq_reading_cards_reading_position"),
    )

    reading_id: Mapped[int] = mapped_column(
        ForeignKey("readings.primary_key", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tarot_card_id: Mapped[int] = mapped_column(
        ForeignKey("tarot_cards.primary_key", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    position_index: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    position_key: Mapped[CardPositionKey] = mapped_column(
        Enum(CardPositionKey, native_enum=False),
        nullable=False,
    )
    is_reversed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    reading: Mapped[Reading] = relationship("Reading", back_populates="cards", lazy="selectin")
    tarot_card: Mapped[TarotCard] = relationship("TarotCard", back_populates="reading_cards", lazy="selectin")
