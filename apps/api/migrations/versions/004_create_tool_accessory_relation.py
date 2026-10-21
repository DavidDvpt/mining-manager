"""create tool accessory relation table

Revision ID: 004_tool_accessory_relation
Revises: 003_create_economy
Create Date: 2026-10-21
"""

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


def downgrade() -> None:
    op.drop_table("tool_accessory_relation")
    sa.Enum(name="tool_compatibility_role").drop(op.get_bind(), checkfirst=True)
