"""Rename product slugs to descriptive URLs (no najd-*-al-* poetry).

Revision ID: 003
Revises: 002
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SLUG_PAIRS: tuple[tuple[str, str], ...] = (
    ("najd-thabat-al-khat", "face-primer"),
    ("najd-darag-al-nahar", "face-sunscreen-spf50"),
    ("najd-safa-al-jabha", "forehead-serum"),
)


def upgrade() -> None:
    conn = op.get_bind()
    for old, new in _SLUG_PAIRS:
        conn.execute(
            sa.text("UPDATE products SET slug = :new WHERE slug = :old"),
            {"old": old, "new": new},
        )
        conn.execute(
            sa.text(
                "UPDATE order_items SET product_slug = :new WHERE product_slug = :old"
            ),
            {"old": old, "new": new},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for old, new in _SLUG_PAIRS:
        conn.execute(
            sa.text("UPDATE products SET slug = :old WHERE slug = :new"),
            {"old": old, "new": new},
        )
        conn.execute(
            sa.text(
                "UPDATE order_items SET product_slug = :old WHERE product_slug = :new"
            ),
            {"old": old, "new": new},
        )
