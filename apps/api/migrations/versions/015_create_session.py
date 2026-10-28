"""create sessions and session lines"""

import sqlalchemy as sa
from alembic import op

revision = "015_create_session"
down_revision = "014_create_lot"
branch_labels = None
depends_on = None


def upgrade() -> None:
    session_line_type = sa.Enum(
        "CONSUMED",
        "PRODUCED",
        name="session_line_type",
    )
    op.create_table(
        "session",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column(
            "started_at",
            sa.Date(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("ended_at", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "session_mining",
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("clic", sa.Integer(), nullable=False),
        sa.CheckConstraint("clic > 0", name="ck_session_mining_clic_positive"),
        sa.ForeignKeyConstraint(
            ["session_id"], ["session.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("session_id"),
    )
    op.create_table(
        "session_refinage",
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("clic", sa.Integer(), nullable=False),
        sa.CheckConstraint("clic > 0", name="ck_session_refinage_clic_positive"),
        sa.ForeignKeyConstraint(
            ["session_id"], ["session.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("session_id"),
    )
    op.create_table(
        "session_transaction",
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column(
            "type",
            sa.Enum("BUY", "SELL", name="session_transaction_type"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "RUNNING",
                "RETURNED",
                "SOLDED",
                "CANCELLED",
                name="session_transaction_status",
            ),
            nullable=False,
        ),
        sa.Column(
            "type_detail",
            sa.Enum(
                "BUY",
                "SELL",
                "FOUND",
                "GIFT",
                "EXISTING_STOCK",
                "GIVEN",
                name="session_transaction_type_detail",
            ),
            nullable=True,
        ),
        sa.CheckConstraint(
            "type = 'BUY' OR type_detail IS NULL",
            name="ck_session_transaction_type_detail_buy_only",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"], ["session.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("session_id"),
    )
    op.create_table(
        "session_line",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("type", session_line_type, nullable=False),
        sa.Column("lot_id", sa.Uuid(), nullable=True, server_default=sa.text("NULL")),
        sa.Column("qty", sa.Integer(), nullable=True, server_default=sa.text("NULL")),
        sa.ForeignKeyConstraint(
            ["session_id"], ["session.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["lot_id"], ["lot.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "session_line_transaction",
        sa.Column("session_line_id", sa.Uuid(), nullable=False),
        sa.Column("tt", sa.Numeric(precision=12, scale=5), nullable=False),
        sa.Column("ttc", sa.Numeric(precision=12, scale=5), nullable=False),
        sa.Column("fee", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_line_id"], ["session_line.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("session_line_id"),
    )
    op.create_table(
        "session_line_decay",
        sa.Column("session_line_id", sa.Uuid(), nullable=False),
        sa.Column("decay_ttc", sa.Numeric(precision=12, scale=5), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_line_id"], ["session_line.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("session_line_id"),
    )


def downgrade() -> None:
    op.drop_table("session_line_decay")
    op.drop_table("session_line_transaction")
    op.drop_table("session_line")
    op.drop_table("session_transaction")
    op.drop_table("session_refinage")
    op.drop_table("session_mining")
    op.drop_table("session")
    sa.Enum(name="session_transaction_type_detail").drop(
        op.get_bind(), checkfirst=True
    )
    sa.Enum(name="session_transaction_status").drop(
        op.get_bind(), checkfirst=True
    )
    sa.Enum(name="session_transaction_type").drop(
        op.get_bind(), checkfirst=True
    )
    sa.Enum(name="session_line_type").drop(op.get_bind(), checkfirst=True)
