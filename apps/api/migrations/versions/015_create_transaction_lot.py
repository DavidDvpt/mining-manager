"""create transaction lot polymorphic link table"""

import sqlalchemy as sa
from alembic import op

revision = "015_create_transaction_lot"
down_revision = "014_create_transaction"
branch_labels = None
depends_on = None


def upgrade() -> None:
    lot_type = sa.Enum(
        "MATERIAL",
        "TOOL",
        "ENHANCER",
        name="transaction_lot_type",
    )
    op.create_table(
        "transaction_lot",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("transaction_id", sa.Uuid(), nullable=False),
        sa.Column("lot_type", lot_type, nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("material_lot_id", sa.Uuid(), nullable=True),
        sa.Column("tool_lot_id", sa.Uuid(), nullable=True),
        sa.Column("enhancer_lot_id", sa.Uuid(), nullable=True),
        sa.CheckConstraint(
            "quantity > 0",
            name="ck_transaction_lot_quantity_positive",
        ),
        sa.CheckConstraint(
            "(lot_type = 'MATERIAL' AND material_lot_id IS NOT NULL "
            "AND tool_lot_id IS NULL AND enhancer_lot_id IS NULL) OR "
            "(lot_type = 'TOOL' AND material_lot_id IS NULL "
            "AND tool_lot_id IS NOT NULL AND enhancer_lot_id IS NULL) OR "
            "(lot_type = 'ENHANCER' AND material_lot_id IS NULL "
            "AND tool_lot_id IS NULL AND enhancer_lot_id IS NOT NULL)",
            name="ck_transaction_lot_single_lot_reference",
        ),
        sa.ForeignKeyConstraint(
            ["transaction_id"], ["transaction.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["material_lot_id"], ["resource_lot.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("transaction_lot")
    sa.Enum(name="transaction_lot_type").drop(op.get_bind(), checkfirst=True)
