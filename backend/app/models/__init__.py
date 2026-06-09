"""
SQLAlchemy-модели домена Таро-бота.

Импорт всех моделей отсюда нужен Alembic (autogenerate) и тестам.
Порядок импорта не важен — связи объявлены через строковые имена.
"""

from app.models.enums import Arcana, CardPositionKey, ReadingStatus, SpreadType, Suit
from app.models.reading import Reading
from app.models.reading_card import ReadingCard
from app.models.tarot_card import TarotCard
from app.models.user import User

__all__ = [
    "Arcana",
    "CardPositionKey",
    "Reading",
    "ReadingCard",
    "ReadingStatus",
    "SpreadType",
    "Suit",
    "TarotCard",
    "User",
]
