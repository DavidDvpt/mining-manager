"""create economy table

Revision ID: 002_create_economy
Revises: 001_create_item
Create Date: 2026-10-21
"""

import sqlalchemy as sa
from alembic import op

revision = "002_create_economy"
down_revision = "001_create_item"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "economy",
        sa.Column("item_id", sa.Uuid(), nullable=False),
        sa.Column("tt", sa.Numeric(), nullable=True),
        sa.Column("decay", sa.Numeric(), nullable=True),
        sa.Column("avg_mu_percent", sa.Numeric(), nullable=True),
        sa.Column("avg_mu_plus", sa.Numeric(), nullable=True),
        sa.ForeignKeyConstraint(["item_id"], ["item.id"]),
        sa.PrimaryKeyConstraint("item_id"),
    )


def downgrade() -> None:
    op.drop_table("economy")
