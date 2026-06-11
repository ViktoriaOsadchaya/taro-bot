"""Общие фикстуры и маркеры pytest."""

from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "unit: unit-тесты без БД, Redis и сети")
