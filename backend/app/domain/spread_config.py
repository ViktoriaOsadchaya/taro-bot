"""
Конфигурация типов раскладов и маппинг позиций карт.

Бизнес-правила «сколько карт нужно» и «какие position_key» живут здесь,
а не в БД — типы раскладов фиксированы на уровне продукта.
"""

from dataclasses import dataclass

from app.models.enums import CardPositionKey, SpreadType


@dataclass(frozen=True, slots=True)
class SpreadDefinition:
    """Описание одного типа расклада для сервисного слоя и API."""

    spread_type: SpreadType
    cards_count: int
    requires_question: bool
    title_ru: str
    description_ru: str


# Ключ — SpreadType, значение — параметры расклада.
SPREAD_DEFINITIONS: dict[SpreadType, SpreadDefinition] = {
    SpreadType.CARD_OF_DAY: SpreadDefinition(
        spread_type=SpreadType.CARD_OF_DAY,
        cards_count=1,
        requires_question=False,
        title_ru="Карта дня",
        description_ru="Одна карта — быстрый совет на сегодня.",
    ),
    SpreadType.PAST_PRESENT_FUTURE: SpreadDefinition(
        spread_type=SpreadType.PAST_PRESENT_FUTURE,
        cards_count=3,
        requires_question=False,
        title_ru="Прошлое, настоящее, будущее",
        description_ru="Три карты — взгляд на ситуацию во времени.",
    ),
    SpreadType.FREE_QUESTION: SpreadDefinition(
        spread_type=SpreadType.FREE_QUESTION,
        cards_count=3,
        requires_question=True,
        title_ru="Свободный вопрос",
        description_ru="Задайте вопрос — три карты дадут ответ.",
    ),
}

# Порядок position_key по индексу карты для каждого типа расклада.
POSITION_KEYS_BY_SPREAD: dict[SpreadType, tuple[CardPositionKey, ...]] = {
    SpreadType.CARD_OF_DAY: (CardPositionKey.DAY,),
    SpreadType.PAST_PRESENT_FUTURE: (
        CardPositionKey.PAST,
        CardPositionKey.PRESENT,
        CardPositionKey.FUTURE,
    ),
    SpreadType.FREE_QUESTION: (
        CardPositionKey.INSIGHT_1,
        CardPositionKey.INSIGHT_2,
        CardPositionKey.INSIGHT_3,
    ),
}

# Человекочитаемые подписи позиций для UI и промпта LLM.
POSITION_LABELS_RU: dict[CardPositionKey, str] = {
    CardPositionKey.DAY: "Карта дня",
    CardPositionKey.PAST: "Прошлое",
    CardPositionKey.PRESENT: "Настоящее",
    CardPositionKey.FUTURE: "Будущее",
    CardPositionKey.INSIGHT_1: "Совет",
    CardPositionKey.INSIGHT_2: "Препятствие",
    CardPositionKey.INSIGHT_3: "Итог",
}


def get_spread_definition(spread_type: SpreadType) -> SpreadDefinition:
    """Возвращает конфиг расклада или выбрасывает KeyError для неизвестного типа."""
    return SPREAD_DEFINITIONS[spread_type]


def get_position_key(spread_type: SpreadType, position_index: int) -> CardPositionKey:
    """Возвращает семантический ключ позиции по типу расклада и индексу карты."""
    keys = POSITION_KEYS_BY_SPREAD[spread_type]
    return keys[position_index]
