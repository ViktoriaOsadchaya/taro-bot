"""
Репозитории проекта: единая точка импорта для container и тестов.
"""

from app.repositories.reading_repository import ReadingRepository, reading_repository
from app.repositories.tarot_card_repository import TarotCardRepository, tarot_card_repository
from app.repositories.user_repository import UserRepository, user_repository

__all__ = [
    "ReadingRepository",
    "TarotCardRepository",
    "UserRepository",
    "reading_repository",
    "tarot_card_repository",
    "user_repository",
]
