"""Справочник 78 карт Rider–Waite для seed-миграции."""

from typing import TypedDict


class TarotCardSeed(TypedDict):
    code: str
    name_ru: str
    name_en: str
    arcana: str
    suit: str | None
    number: int | None
    image_path: str


_MAJOR: list[tuple[int, str, str, str]] = [
    (0, "fool", "Шут", "The Fool"),
    (1, "magician", "Маг", "The Magician"),
    (2, "high_priestess", "Жрица", "The High Priestess"),
    (3, "empress", "Императрица", "The Empress"),
    (4, "emperor", "Император", "The Emperor"),
    (5, "hierophant", "Иерофант", "The Hierophant"),
    (6, "lovers", "Влюблённые", "The Lovers"),
    (7, "chariot", "Колесница", "The Chariot"),
    (8, "strength", "Сила", "Strength"),
    (9, "hermit", "Отшельник", "The Hermit"),
    (10, "wheel_of_fortune", "Колесо Фортуны", "Wheel of Fortune"),
    (11, "justice", "Справедливость", "Justice"),
    (12, "hanged_man", "Повешенный", "The Hanged Man"),
    (13, "death", "Смерть", "Death"),
    (14, "temperance", "Умеренность", "Temperance"),
    (15, "devil", "Дьявол", "The Devil"),
    (16, "tower", "Башня", "The Tower"),
    (17, "star", "Звезда", "The Star"),
    (18, "moon", "Луна", "The Moon"),
    (19, "sun", "Солнце", "The Sun"),
    (20, "judgement", "Суд", "Judgement"),
    (21, "world", "Мир", "The World"),
]

_SUITS: list[tuple[str, str, str]] = [
    ("wands", "Жезлов", "Wands"),
    ("cups", "Кубков", "Cups"),
    ("swords", "Мечей", "Swords"),
    ("pentacles", "Пентаклей", "Pentacles"),
]

_RANKS: list[tuple[str, int, str, str]] = [
    ("ace", 1, "Туз", "Ace"),
    ("02", 2, "Двойка", "Two"),
    ("03", 3, "Тройка", "Three"),
    ("04", 4, "Четвёрка", "Four"),
    ("05", 5, "Пятёрка", "Five"),
    ("06", 6, "Шестёрка", "Six"),
    ("07", 7, "Семёрка", "Seven"),
    ("08", 8, "Восьмёрка", "Eight"),
    ("09", 9, "Девятка", "Nine"),
    ("10", 10, "Десятка", "Ten"),
    ("page", 11, "Паж", "Page"),
    ("knight", 12, "Рыцарь", "Knight"),
    ("queen", 13, "Королева", "Queen"),
    ("king", 14, "Король", "King"),
]


def build_tarot_card_seeds() -> list[TarotCardSeed]:
    """Возвращает 78 записей: code совпадает с именем файла в public/cards/."""
    cards: list[TarotCardSeed] = []

    for number, slug, name_ru, name_en in _MAJOR:
        code = f"major_{number:02d}_{slug}"
        cards.append(
            {
                "code": code,
                "name_ru": name_ru,
                "name_en": name_en,
                "arcana": "major",
                "suit": None,
                "number": number,
                "image_path": f"/cards/{code}.jpg",
            }
        )

    for suit_code, suit_ru_gen, suit_en in _SUITS:
        for rank_code, number, rank_ru, rank_en in _RANKS:
            code = f"{suit_code}_{rank_code}"
            cards.append(
                {
                    "code": code,
                    "name_ru": f"{rank_ru} {suit_ru_gen}",
                    "name_en": f"{rank_en} of {suit_en}",
                    "arcana": "minor",
                    "suit": suit_code,
                    "number": number,
                    "image_path": f"/cards/{code}.jpg",
                }
            )

    return cards


TAROT_CARDS_RIDER_WAITE: list[TarotCardSeed] = build_tarot_card_seeds()
