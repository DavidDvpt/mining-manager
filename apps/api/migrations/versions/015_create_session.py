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
        sa.CheckConstraint(
            "qty IS NULL OR qty >= 0",
            name="ck_session_line_qty_non_negative",
        ),
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
        sa.CheckConstraint(
            "decay_ttc >= 0",
            name="ck_session_line_decay_non_negative",
        ),
        sa.ForeignKeyConstraint(
            ["session_line_id"], ["session_line.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("session_line_id"),
    )
    op.execute(
        """
        CREATE FUNCTION enforce_session_immutability()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF NEW.id IS DISTINCT FROM OLD.id
                OR NEW.user_id IS DISTINCT FROM OLD.user_id
                OR NEW.started_at IS DISTINCT FROM OLD.started_at
                OR (
                    OLD.ended_at IS NOT NULL
                    AND NEW.ended_at IS DISTINCT FROM OLD.ended_at
                )
            THEN
                RAISE EXCEPTION
                    'Session data is immutable; ended_at can only be set once';
            END IF;
            RETURN NEW;
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE TRIGGER enforce_session_immutability_trigger
        BEFORE UPDATE ON session
        FOR EACH ROW EXECUTE FUNCTION enforce_session_immutability();
        """
    )
    op.execute(
        """
        CREATE FUNCTION enforce_session_line_update()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        DECLARE
            available_quantity integer;
            used_quantity integer;
        BEGIN
            IF NEW.id IS DISTINCT FROM OLD.id
                OR NEW.session_id IS DISTINCT FROM OLD.session_id
                OR NEW.item_id IS DISTINCT FROM OLD.item_id
                OR NEW.type IS DISTINCT FROM OLD.type
                OR NEW.lot_id IS DISTINCT FROM OLD.lot_id
            THEN
                RAISE EXCEPTION 'Session line identity and type are immutable';
            END IF;

            IF NEW.qty IS NOT DISTINCT FROM OLD.qty THEN
                RETURN NEW;
            END IF;

            IF NOT EXISTS (
                SELECT 1
                FROM session
                WHERE session.id = NEW.session_id
                    AND session.ended_at IS NULL
            )
            THEN
                RAISE EXCEPTION 'Only an open session can change line quantity';
            END IF;

            IF current_setting('app.session_line_update_mode', true)
                = 'produced_qty'
            THEN
                IF NEW.type <> 'PRODUCED'
                    OR NEW.item_id IS NULL
                    OR NEW.lot_id IS NOT NULL
                    OR NEW.qty < 0
                THEN
                    RAISE EXCEPTION
                        'Only produced line quantity can be changed here';
                END IF;
                RETURN NEW;
            END IF;

            IF current_setting('app.session_line_update_mode', true)
                NOT IN ('enhancer_qty', 'close')
                OR NEW.type <> 'CONSUMED'
                OR NEW.item_id IS NOT NULL
                OR NEW.lot_id IS NULL
                OR NEW.qty < 0
                OR (
                    current_setting('app.session_line_update_mode', true)
                        = 'enhancer_qty'
                    AND NEW.qty < OLD.qty
                )
                OR NOT EXISTS (
                    SELECT 1
                    FROM lot
                    JOIN session_line origin_line
                        ON origin_line.id::text = lot.origin_id
                    JOIN enhancer
                        ON enhancer.item_id = origin_line.item_id
                    WHERE lot.id = NEW.lot_id
                        AND lot.user_id = (
                            SELECT user_id
                            FROM session
                            WHERE id = NEW.session_id
                        )
                )
            THEN
                RAISE EXCEPTION 'Only enhancer quantity can be changed here';
            END IF;

            SELECT lot.qty - lot.reserved
            INTO available_quantity
            FROM lot
            WHERE lot.id = NEW.lot_id;

            SELECT coalesce(sum(session_line.qty), 0)
            INTO used_quantity
            FROM session_line
            WHERE session_line.lot_id = NEW.lot_id
                AND session_line.id <> NEW.id;

            IF NEW.qty + used_quantity > available_quantity THEN
                RAISE EXCEPTION 'Enhancer quantity exceeds available stock';
            END IF;

            RETURN NEW;
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE TRIGGER enforce_session_line_update_trigger
        BEFORE UPDATE ON session_line
        FOR EACH ROW EXECUTE FUNCTION enforce_session_line_update();
        """
    )
    op.execute(
        """
        CREATE FUNCTION enforce_session_line_decay_update()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF NEW.session_line_id IS DISTINCT FROM OLD.session_line_id THEN
                RAISE EXCEPTION 'Session line decay identity is immutable';
            END IF;

            IF current_setting('app.session_line_update_mode', true) <> 'close'
                OR NOT EXISTS (
                    SELECT 1
                    FROM session_line
                    LEFT JOIN item direct_item
                        ON direct_item.id = session_line.item_id
                    LEFT JOIN lot
                        ON lot.id = session_line.lot_id
                    LEFT JOIN session_line origin_line
                        ON origin_line.id::text = lot.origin_id
                    LEFT JOIN item origin_item
                        ON origin_item.id = origin_line.item_id
                    LEFT JOIN finder
                        ON finder.item_id = coalesce(
                            direct_item.id, origin_item.id
                        )
                    LEFT JOIN excavator
                        ON excavator.item_id = coalesce(
                            direct_item.id, origin_item.id
                        )
                    LEFT JOIN finder_amplifier
                        ON finder_amplifier.item_id = coalesce(
                            direct_item.id, origin_item.id
                        )
                    WHERE session_line.id = NEW.session_line_id
                        AND (
                            finder.item_id IS NOT NULL
                            OR excavator.item_id IS NOT NULL
                            OR finder_amplifier.item_id IS NOT NULL
                        )
                )
            THEN
                RAISE EXCEPTION 'Only closing may update excavator decay';
            END IF;

            RETURN NEW;
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE TRIGGER enforce_session_line_decay_update_trigger
        BEFORE UPDATE ON session_line_decay
        FOR EACH ROW EXECUTE FUNCTION enforce_session_line_decay_update();
        """
    )
    op.execute(
        """
        CREATE FUNCTION prevent_session_line_delete_with_lot()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM lot
                WHERE lot.origin_id = OLD.id::text
            )
            THEN
                RAISE EXCEPTION
                    'A session line with an originating lot cannot be deleted';
            END IF;
            RETURN OLD;
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE TRIGGER prevent_session_line_delete_with_lot_trigger
        BEFORE DELETE ON session_line
        FOR EACH ROW EXECUTE FUNCTION prevent_session_line_delete_with_lot();
        """
    )

def downgrade() -> None:
    op.execute(
        """
        DROP TRIGGER IF EXISTS prevent_session_line_delete_with_lot_trigger
        ON session_line
        """
    )
    op.execute("DROP FUNCTION IF EXISTS prevent_session_line_delete_with_lot()")
    op.execute(
        """
        DROP TRIGGER IF EXISTS enforce_session_line_decay_update_trigger
        ON session_line_decay
        """
    )
    op.execute("DROP FUNCTION IF EXISTS enforce_session_line_decay_update()")
    op.execute(
        "DROP TRIGGER IF EXISTS enforce_session_line_update_trigger ON session_line"
    )
    op.execute("DROP FUNCTION IF EXISTS enforce_session_line_update()")
    op.execute(
        "DROP TRIGGER IF EXISTS enforce_session_immutability_trigger ON session"
    )
    op.execute("DROP FUNCTION IF EXISTS enforce_session_immutability()")
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
