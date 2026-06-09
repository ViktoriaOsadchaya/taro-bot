"""
Шаблоны промптов для InterpretationService.

Чистые функции без I/O — только формирование текста для LLM.
"""

from app.api.schemas.reading_session_dto import DrawnCardSessionDTO
from app.domain.spread_config import POSITION_LABELS_RU, get_spread_definition
from app.models.enums import SpreadType


def build_system_prompt() -> str:
    """System prompt: стиль таинственного мудрого таролога."""
    return (
        "Ты — опытный таролог с глубоким знанием символики Таро. "
        "Отвечай на русском языке в стиле мудрого, таинственного, но доброжелательного наставника. "
        "Не упоминай, что ты искусственный интеллект. "
        "Не давай медицинских, юридических или финансовых директив — только символическое толкование. "
        "Структурируй ответ: краткое вступление, толкование каждой карты с учётом позиции и перевёрнутости, "
        "затем общий вывод. Объём — 300–600 слов."
    )


def build_user_prompt(
    spread_type: SpreadType,
    question: str | None,
    drawn_cards: list[DrawnCardSessionDTO],
) -> str:
    """
    User prompt: тип расклада, вопрос (если есть) и список выпавших карт.

    ***drawn_cards: уже вытянутые карты с position_key и is_reversed***
    """
    spread = get_spread_definition(spread_type)
    lines = [
        f"Тип расклада: {spread.title_ru}",
        f"Описание: {spread.description_ru}",
    ]
    if question:
        lines.append(f"Вопрос пользователя: {question}")
    lines.append("")
    lines.append("Выпавшие карты:")
    for card in drawn_cards:
        orientation = "перевёрнутая" if card.is_reversed else "прямая"
        label = POSITION_LABELS_RU.get(card.position_key, card.position_key.value)
        lines.append(
            f"- Позиция «{label}»: {card.name_ru} ({orientation})"
        )
    lines.append("")
    lines.append("Дай цельное толкование этого расклада.")
    return "\n".join(lines)
