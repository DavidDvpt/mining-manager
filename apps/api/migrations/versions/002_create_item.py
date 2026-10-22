"""create item table

Revision ID: 002_create_item
Revises: 001_create_type
Create Date: 2026-10-21
"""

import sqlalchemy as sa
from alembic import op

revision = "002_create_item"
down_revision = "001_create_type"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "item",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("img_id", sa.Integer(), nullable=True),
        sa.Column("weight", sa.Numeric(), nullable=True),
        sa.Column(
            "is_untradeable",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=True,
        ),
        sa.Column(
            "is_rare",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=True,
        ),
        sa.Column("nexus_url", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("type_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["type_id"], ["type.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )


def downgrade() -> None:
    op.drop_table("item")
