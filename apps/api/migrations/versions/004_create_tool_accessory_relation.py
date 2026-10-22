"""create tool accessory relation table

Revision ID: 004_tool_accessory_relation
Revises: 003_create_economy
Create Date: 2026-10-21
"""

from uuid import UUID

import sqlalchemy as sa
from alembic import op

revision = "004_tool_accessory_relation"
down_revision = "003_create_economy"
branch_labels = None
depends_on = None


def upgrade() -> None:
    tool_compatibility_role = sa.Enum(
        "AMPLIFIER",
        "ENHANCER",
        name="tool_compatibility_role",
        create_type=False,
    )
    tool_compatibility_role.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "tool_accessory_relation",
        sa.Column("tool_type_id", sa.Uuid(), nullable=False),
        sa.Column("accessory_type_id", sa.Uuid(), nullable=False),
        sa.Column("role", tool_compatibility_role, nullable=False),
        sa.ForeignKeyConstraint(["tool_type_id"], ["type.id"]),
        sa.ForeignKeyConstraint(["accessory_type_id"], ["type.id"]),
        sa.PrimaryKeyConstraint("tool_type_id", "accessory_type_id"),
    )

    relation_table = sa.table(
        "tool_accessory_relation",
        sa.column("tool_type_id", sa.Uuid()),
        sa.column("accessory_type_id", sa.Uuid()),
        sa.column("role", tool_compatibility_role),
    )
    op.bulk_insert(
        relation_table,
        [
            {
                "tool_type_id": UUID("3cf59ae8-0a13-4dac-9b9e-e0f6824a082f"),
                "accessory_type_id": UUID("549a7d53-f04a-4da9-baa8-b6fae2f4966f"),
                "role": "AMPLIFIER",
            },
            {
                "tool_type_id": UUID("3cf59ae8-0a13-4dac-9b9e-e0f6824a082f"),
                "accessory_type_id": UUID("155f05ef-29b7-478a-aaa7-7d8db93e8811"),
                "role": "ENHANCER",
            },
            {
                "tool_type_id": UUID("a81ff2c2-6d26-49bd-9dd7-73c38c64773d"),
                "accessory_type_id": UUID("155f05ef-29b7-478a-aaa7-7d8db93e8811"),
                "role": "ENHANCER",
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("tool_accessory_relation")
    sa.Enum(name="tool_compatibility_role").drop(op.get_bind(), checkfirst=True)
