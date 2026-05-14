"""Rename product Arabic display names to short poetic names (no brand prefix).

Revision ID: 005
Revises: 004
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (slug, old_name_ar, new_name_ar)
_NAME_PAIRS: tuple[tuple[str, str, str], ...] = (
    ("face-primer", "برايمر الوجه", "ثبات الخط"),
    ("face-sunscreen-spf50", "واقي شمس للوجه SPF 50+", "درع النهار"),
    ("forehead-serum", "سيروم الجبهة", "صفاء الجبهة"),
)


def upgrade() -> None:
    conn = op.get_bind()
    for slug, _old, new in _NAME_PAIRS:
        conn.execute(
            sa.text("UPDATE products SET name_ar = :new WHERE slug = :slug"),
            {"slug": slug, "new": new},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for slug, old, _new in _NAME_PAIRS:
        conn.execute(
            sa.text("UPDATE products SET name_ar = :old WHERE slug = :slug"),
            {"slug": slug, "old": old},
        )
