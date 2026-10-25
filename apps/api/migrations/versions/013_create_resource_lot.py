"""create resource lot table"""

import sqlalchemy as sa
from alembic import op

revision = "013_create_resource_lot"
down_revision = "012_create_profile"
branch_labels = None
depends_on = None


def upgrade() -> None:
    origin = sa.Enum(
        "MINING",
        "REFINING",
        "TRADE",
        name="resource_lot_origin",
    )
    origin_type = sa.Enum(
        "TRANSACTION",
        "SESSION_LINE",
        name="resource_lot_origin_type",
    )
    op.create_table(
        "resource_lot",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("item_id", sa.Uuid(), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column(
            "ratio_source",
            sa.Numeric(precision=20, scale=5),
            server_default=sa.text("1"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("transaction_id", sa.Uuid(), nullable=True),
        sa.Column("session_line_id", sa.Uuid(), nullable=True),
        sa.Column("origin", origin, nullable=False),
        sa.Column("origin_type", origin_type, nullable=False),
        sa.CheckConstraint("qty >= 0", name="ck_resource_lot_qty_non_negative"),
        sa.CheckConstraint(
            "(origin_type = 'TRANSACTION' AND transaction_id IS NOT NULL "
            "AND session_line_id IS NULL) OR "
            "(origin_type = 'SESSION_LINE' AND transaction_id IS NULL "
            "AND session_line_id IS NOT NULL)",
            name="ck_resource_lot_single_origin",
        ),
        sa.ForeignKeyConstraint(["item_id"], ["material.item_id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("resource_lot")
    sa.Enum(name="resource_lot_origin").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="resource_lot_origin_type").drop(op.get_bind(), checkfirst=True)
