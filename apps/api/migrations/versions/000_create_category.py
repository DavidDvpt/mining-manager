"""create category table and initial categories

Revision ID: 000_create_category
Revises:
Create Date: 2026-10-20
"""

from datetime import datetime, timezone
from uuid import UUID

from alembic import op
import sqlalchemy as sa


revision = "000_create_category"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "category",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    category = sa.table(
        "category",
        sa.column("id", sa.Uuid()),
        sa.column("name", sa.String()),
        sa.column("is_active", sa.Boolean()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )

    op.bulk_insert(
        category,
        [
            {
                "id": UUID("88B86318-0F7B-4D68-B095-D0DC313324A5"),
                "name": "Material",
                "is_active": True,
                "created_at": datetime(2025, 11, 23, 11, 59, 1, 595717),
                "updated_at": None,
            },
            {
                "id": UUID("761d24c4-8bc5-42e2-b30d-b749bc4d3eb4"),
                "name": "Tool",
                "is_active": True,
                "created_at": datetime(
                    2026, 10, 7, 16, 49, 31, 120000, tzinfo=timezone.utc
                ),
                "updated_at": None,
            },
        ],
    )

    category_with_defaults = sa.table(
        "category",
        sa.column("name", sa.String()),
        sa.column("is_active", sa.Boolean()),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    op.bulk_insert(
        category_with_defaults,
        [
            {
                "name": "Accessory",
                "is_active": True,
                "updated_at": None,
            }
        ],
    )


def downgrade() -> None:
    op.drop_table("category")
