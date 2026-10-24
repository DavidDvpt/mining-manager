"""create material type table and seed material types

Revision ID: 008_create_material_type
Revises: 007_remove_type_system
Create Date: 2026-10-24
"""

import sqlalchemy as sa
from alembic import op

revision = "008_create_material_type"
down_revision = "007_remove_type_system"
branch_labels = None
depends_on = None


MATERIAL_TYPES = [
    "Enmatter",
    "Ore",
    "Refined Enmatter",
    "Refined Ore",
    "Food",
    "Natural Material",
    "Fragment",
    "consumable",
    "Animal oil",
]


def upgrade() -> None:
    op.create_table(
        "material_type",
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    material_type_table = sa.table(
        "material_type",
        sa.column("name", sa.String(length=255)),
    )
    op.bulk_insert(
        material_type_table,
        [{"name": name} for name in MATERIAL_TYPES],
    )


def downgrade() -> None:
    op.drop_table("material_type")
