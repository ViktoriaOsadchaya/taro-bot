"""Unit-тесты доменной конфигурации раскладов."""

from __future__ import annotations

import pytest

from app.domain.spread_config import (
    SPREAD_DEFINITIONS,
    get_position_key,
    get_spread_definition,
)
from app.models.enums import CardPositionKey, SpreadType
from tests.unit.base import UnitTestCase


class TestSpreadConfig(UnitTestCase):
    def test_all_spread_types_have_definition(self) -> None:
        for spread_type in SpreadType:
            definition = get_spread_definition(spread_type)
            assert definition.spread_type is spread_type
            assert definition.cards_count > 0

    def test_past_present_future_positions(self) -> None:
        spread = get_spread_definition(SpreadType.PAST_PRESENT_FUTURE)
        assert spread.cards_count == 3
        assert spread.requires_question is False
        assert get_position_key(SpreadType.PAST_PRESENT_FUTURE, 0) is CardPositionKey.PAST
        assert get_position_key(SpreadType.PAST_PRESENT_FUTURE, 2) is CardPositionKey.FUTURE

    def test_free_question_requires_question(self) -> None:
        spread = get_spread_definition(SpreadType.FREE_QUESTION)
        assert spread.requires_question is True
        assert spread.title_ru == "Свободный вопрос"

    def test_position_index_out_of_range_raises(self) -> None:
        with pytest.raises(IndexError):
            get_position_key(SpreadType.CARD_OF_DAY, 1)

    def test_definitions_match_spread_types_count(self) -> None:
        assert len(SPREAD_DEFINITIONS) == len(SpreadType)
