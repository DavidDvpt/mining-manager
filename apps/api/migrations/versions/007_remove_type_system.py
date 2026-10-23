"""remove the legacy item type system

Revision ID: 007_remove_type_system
Revises: 006_create_enhancer
Create Date: 2026-10-23
"""

import sqlalchemy as sa
from alembic import op

revision = "007_remove_type_system"
down_revision = "006_create_enhancer"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "item" in tables:
        item_columns = {column["name"] for column in inspector.get_columns("item")}
        if "type_id" in item_columns:
            for foreign_key in inspector.get_foreign_keys("item"):
                if (
                    "type_id" in foreign_key["constrained_columns"]
                    and foreign_key["name"]
                ):
                    op.drop_constraint(
                        foreign_key["name"], "item", type_="foreignkey"
                    )
            op.drop_column("item", "type_id")

    for table_name in ("tool_accessory_relation", "type", "category"):
        if table_name in tables:
            op.drop_table(table_name)


def downgrade() -> None:
    pass
