from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base
from app.models.enums import ReadingStatus, SpreadType, str_enum

if TYPE_CHECKING:
    from app.models.reading_card import ReadingCard
    from app.models.user import User


class Reading(Base):
    """
    Завершённый или неудачный расклад пользователя.

    Черновики и пошаговый выбор карт живут в Redis (ReadingSessionService).
    В PostgreSQL попадает только финальный результат после вызова LLM.
    """

    __table_args__ = (
        # Составной индекс для /history: выборка по user_id с сортировкой по дате.
        Index("ix_readings_user_id_created_at", "user_id", "created_at"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.primary_key", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    spread_type: Mapped[SpreadType] = mapped_column(str_enum(SpreadType), nullable=False)
    # Заполняется только для SpreadType.FREE_QUESTION.
    question: Mapped[str | None] = mapped_column(Text, nullable=True)
    interpretation: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ReadingStatus] = mapped_column(str_enum(ReadingStatus), nullable=False)
    llm_model: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship("User", back_populates="readings", lazy="selectin")
    cards: Mapped[list[ReadingCard]] = relationship(
        "ReadingCard",
        back_populates="reading",
        lazy="selectin",
        order_by="ReadingCard.position_index",
        cascade="all, delete-orphan",
    )
