from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base

if TYPE_CHECKING:
    from app.models.reading import Reading


class User(Base):
    """
    Telegram-пользователь бота.

    Создаётся или обновляется при /start и используется для привязки истории раскладов.
    Идентификация в Telegram — по telegram_id (не по primary_key).
    """

    # Уникальный ID из Telegram API; BigInteger — т.к. id может превышать int32.
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Язык интерфейса и промптов; по умолчанию русский.
    language_code: Mapped[str] = mapped_column(String(10), nullable=False, default="ru", server_default="ru")

    # Завершённые расклады пользователя (lazy=selectin — типичная загрузка для истории).
    readings: Mapped[list[Reading]] = relationship(
        "Reading",
        back_populates="user",
        lazy="selectin",
    )
