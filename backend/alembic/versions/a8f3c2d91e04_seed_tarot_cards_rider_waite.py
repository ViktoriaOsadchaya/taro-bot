"""seed 78 tarot cards rider waite

Revision ID: a8f3c2d91e04
Revises: e5b6d493b126
Create Date: 2026-06-30 17:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.domain.tarot_deck_seed import TAROT_CARDS_RIDER_WAITE

# revision identifiers, used by Alembic.
revision: str = "a8f3c2d91e04"
down_revision: Union[str, Sequence[str], None] = "e5b6d493b126"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TAROT_CODES = [card["code"] for card in TAROT_CARDS_RIDER_WAITE]


def upgrade() -> None:
    """Наполняет tarot_cards колодой Rider–Waite (78 карт)."""
    bind = op.get_bind()
    table = sa.table(
        "tarot_cards",
        sa.column("code", sa.String),
        sa.column("name_ru", sa.String),
        sa.column("name_en", sa.String),
        sa.column("arcana", sa.String),
        sa.column("suit", sa.String),
        sa.column("number", sa.SmallInteger),
        sa.column("image_path", sa.String),
    )

    for card in TAROT_CARDS_RIDER_WAITE:
        stmt = (
            sa.dialects.postgresql.insert(table)
            .values(**card)
            .on_conflict_do_update(
                index_elements=["code"],
                set_={
                    "name_ru": card["name_ru"],
                    "name_en": card["name_en"],
                    "arcana": card["arcana"],
                    "suit": card["suit"],
                    "number": card["number"],
                    "image_path": card["image_path"],
                },
            )
        )
        bind.execute(stmt)


def downgrade() -> None:
    """Удаляет seed-карты Rider–Waite (если на них нет ссылок из reading_cards)."""
    codes_sql = ", ".join(f"'{code}'" for code in TAROT_CODES)
    op.execute(f"DELETE FROM tarot_cards WHERE code IN ({codes_sql})")
