"""create transaction table"""

import sqlalchemy as sa
from alembic import op

revision = "014_create_transaction"
down_revision = "013_create_resource_lot"
branch_labels = None
depends_on = None


def upgrade() -> None:
    transaction_type = sa.Enum(
        "BUY",
        "FOUND",
        "GIFT",
        "EXISTING_STOCK",
        "SELL",
        "GIVEN",
        name="transaction_type",
    )
    transaction_status = sa.Enum(
        "SOLDED",
        "RETURNED",
        "RUNNING",
        "CANCELED",
        name="transaction_status",
    )
    op.create_table(
        "transaction",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "tt",
            sa.Numeric(precision=20, scale=5),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "fee",
            sa.Numeric(precision=20, scale=5),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "ttc",
            sa.Numeric(precision=20, scale=5),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("transaction_type", transaction_type, nullable=False),
        sa.Column("status", transaction_status, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("transaction")
    sa.Enum(name="transaction_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="transaction_status").drop(op.get_bind(), checkfirst=True)
