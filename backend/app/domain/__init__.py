"""Доменные константы и чистая бизнес-логика без доступа к БД и HTTP."""

from app.domain.spread_config import (
    POSITION_KEYS_BY_SPREAD,
    POSITION_LABELS_RU,
    SPREAD_DEFINITIONS,
    SpreadDefinition,
    get_position_key,
    get_spread_definition,
)

__all__ = [
    "POSITION_KEYS_BY_SPREAD",
    "POSITION_LABELS_RU",
    "SPREAD_DEFINITIONS",
    "SpreadDefinition",
    "get_position_key",
    "get_spread_definition",
]
