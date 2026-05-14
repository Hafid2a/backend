"""Add validated click events for admin analytics.

Revision ID: 004
Revises: 003
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "click_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_id", sa.String(), nullable=False),
        sa.Column("client_ip", sa.String(), nullable=True),
        sa.Column("country_code", sa.String(), nullable=True),
        sa.Column("is_valid_ksa_ip", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("ip_check_provider", sa.String(), nullable=True),
        sa.Column("ip_reject_reason", sa.Text(), nullable=True),
        sa.Column("landing_page", sa.Text(), nullable=True),
        sa.Column("referrer", sa.Text(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("utm_source", sa.String(), nullable=True),
        sa.Column("utm_medium", sa.String(), nullable=True),
        sa.Column("utm_campaign", sa.String(), nullable=True),
        sa.Column("utm_content", sa.String(), nullable=True),
        sa.Column("utm_term", sa.String(), nullable=True),
        sa.Column("fbclid", sa.String(), nullable=True),
        sa.Column("ttclid", sa.String(), nullable=True),
        sa.Column("sc_click_id", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_click_events"),
        sa.UniqueConstraint("event_id", name="uq_click_events_event_id"),
    )
    op.create_index("ix_click_events_event_id", "click_events", ["event_id"])
    op.create_index("ix_click_events_is_valid_ksa_ip", "click_events", ["is_valid_ksa_ip"])
    op.create_index("ix_click_events_created_at", "click_events", ["created_at"])
    op.create_index(
        "ix_click_events_created_valid",
        "click_events",
        ["created_at", "is_valid_ksa_ip"],
    )
    op.create_index("ix_click_events_utm_campaign", "click_events", ["utm_campaign"])


def downgrade() -> None:
    op.drop_table("click_events")
