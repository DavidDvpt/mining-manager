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
    session_mining_search_type = sa.Enum(
        "E",
        "O",
        "T",
        "EO",
        "ET",
        "OT",
        "EOT",
        name="session_mining_search_type",
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
        sa.Column("session_sone_id", sa.Uuid(), nullable=True),
        sa.Column("search_type", session_mining_search_type, nullable=False),
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
            sa.Enum(
                "BUY",
                "SELL",
                "CONSUMED",
                name="session_transaction_type",
            ),
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
                "TT",
                "AUCTION",
                "HAND_TO_HAND",
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
        sa.Column("item_id", sa.Uuid(), nullable=True),
        sa.Column("type", session_line_type, nullable=False),
        sa.Column("lot_id", sa.Uuid(), nullable=True, server_default=sa.text("NULL")),
        sa.Column("qty", sa.Integer(), nullable=True, server_default=sa.text("NULL")),
        sa.ForeignKeyConstraint(
            ["session_id"], ["session.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["item_id"], ["item.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["lot_id"], ["lot.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_session_line_item_id", "session_line", ["item_id"])
    op.execute(
        """
        CREATE FUNCTION enforce_session_line_item_lot()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF NEW.type = 'PRODUCED' THEN
                IF NEW.item_id IS NULL OR NEW.lot_id IS NOT NULL THEN
                    RAISE EXCEPTION
                        'A produced session line requires item_id and no lot_id';
                END IF;
            ELSIF NEW.type = 'CONSUMED' THEN
                IF (NEW.lot_id IS NULL AND NEW.item_id IS NULL)
                    OR (NEW.lot_id IS NOT NULL AND NEW.item_id IS NOT NULL) THEN
                    RAISE EXCEPTION
                        'A consumed session line requires either lot_id or item_id';
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE TRIGGER enforce_session_line_item_lot_trigger
        BEFORE INSERT OR UPDATE OF type, item_id, lot_id ON session_line
        FOR EACH ROW EXECUTE FUNCTION enforce_session_line_item_lot();
        """
    )
    op.create_table(
        "session_line_transaction",
        sa.Column("session_line_id", sa.Uuid(), nullable=False),
        sa.Column("tt", sa.Numeric(precision=12, scale=5), nullable=False),
        sa.Column("ttc", sa.Numeric(precision=12, scale=5), nullable=False),
        sa.Column("fee", sa.Numeric(precision=5, scale=2), nullable=True),
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
    op.execute(
        "DROP TRIGGER IF EXISTS enforce_session_line_item_lot_trigger ON session_line"
    )
    op.execute("DROP FUNCTION IF EXISTS enforce_session_line_item_lot()")
    op.drop_index("ix_session_line_item_id", table_name="session_line")
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
    sa.Enum(name="session_mining_search_type").drop(
        op.get_bind(), checkfirst=True
    )
