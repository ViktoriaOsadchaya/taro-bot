"""Базовый класс unit-тестов (пакет ``tests/unit``, вне ``app``)."""

from __future__ import annotations

import pytest


class UnitTestCase:
    """
    Базовый подкласс для unit-тестов.

    Наследуйте от него тест-классы, которые не требуют БД, Redis или HTTP.
    Автоматически помечает тесты маркером ``unit``.
    """

    pytestmark = pytest.mark.unit
