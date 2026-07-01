"""
Доменные перечисления для бота Таро.

Хранятся как str-enum, чтобы значения совпадали с колонками БД (native_enum=False)
и были читаемы в JSON/API без дополнительного маппинга.
"""

from enum import StrEnum

from sqlalchemy import Enum


def str_enum(enum_cls: type[StrEnum]) -> Enum:
    """SQLAlchemy Enum для StrEnum: в БД хранятся .value (card_of_day), не имена (CARD_OF_DAY)."""
    return Enum(
        enum_cls,
        values_callable=lambda members: [member.value for member in members],
        native_enum=False,
    )


class SpreadType(StrEnum):
    """
    Тип расклада, который выбирает пользователь при старте.

    CARD_OF_DAY — 1 карта, быстрый совет на день.
    PAST_PRESENT_FUTURE — классический расклад из 3 карт.
    FREE_QUESTION — 3 карты + текстовый вопрос пользователя.
    """

    CARD_OF_DAY = "card_of_day"
    PAST_PRESENT_FUTURE = "past_present_future"
    FREE_QUESTION = "free_question"


class ReadingStatus(StrEnum):
    """
    Статус сохранённого расклада в PostgreSQL.

    PENDING — расклад создан, ожидает начала генерации.
    GENERATING — LLM генерирует толкование, interpretation пока пустой.
    COMPLETED — толкование получено и сохранено.
    FAILED — ошибка LLM или финализации.
    """

    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class Arcana(StrEnum):
    """Старшие (22) или младшие (56) арканы колоды."""

    MAJOR = "major"
    MINOR = "minor"


class Suit(StrEnum):
    """Масть младших арканов. Для старших арканов в TarotCard.suit = NULL."""

    WANDS = "wands"
    CUPS = "cups"
    SWORDS = "swords"
    PENTACLES = "pentacles"


class CardPositionKey(StrEnum):
    """
    Семантическая роль карты в раскладе (для промпта LLM и UI).

    DAY — единственная карта в «Карте дня».
    PAST/PRESENT/FUTURE — расклад «Прошлое — Настоящее — Будущее».
    INSIGHT_1..3 — альтернативные позиции для «Свободного вопроса».
    """

    DAY = "day"
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"
    INSIGHT_1 = "insight_1"
    INSIGHT_2 = "insight_2"
    INSIGHT_3 = "insight_3"
