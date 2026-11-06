"""create lot and lot specialization tables"""

import sqlalchemy as sa
from alembic import op

revision = "014_create_lot"
down_revision = "013_create_deposit_size"
branch_labels = None
depends_on = None


def upgrade() -> None:
    lot_and_session_type = sa.Enum(
        "MINING",
        "REFINING",
        "TRANSACTION",
        "CRAFTING",
        name="lot_type",
    )
    op.create_table(
        "lot",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("type", lot_and_session_type, nullable=False),
        sa.Column("origin_id", sa.String(), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column(
            "reserved",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.CheckConstraint("qty >= 0", name="ck_lot_qty_non_negative"),
        sa.CheckConstraint(
            "reserved >= 0 AND reserved <= qty",
            name="ck_lot_reserved_between_zero_and_qty",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "material_lot",
        sa.Column("lot_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["lot_id"], ["lot.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("lot_id"),
    )
    op.create_table(
        "tool_lot",
        sa.Column("lot_id", sa.Uuid(), nullable=False),
        sa.Column("tier", sa.Integer(), nullable=True),
        sa.Column("tt", sa.Numeric(precision=20, scale=5), nullable=True),
        sa.Column(
            "is_default",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "tier >= 0 AND tier <= 10",
            name="ck_tool_lot_tier_between_0_and_10",
        ),
        sa.ForeignKeyConstraint(["lot_id"], ["lot.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("lot_id"),
    )
    op.create_table(
        "enhancer_lot",
        sa.Column("lot_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["lot_id"], ["lot.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("lot_id"),
    )
    op.execute(
        """
        CREATE FUNCTION enforce_tool_lot_single_quantity()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF TG_TABLE_NAME = 'tool_lot' THEN
                IF NOT EXISTS (
                    SELECT 1 FROM lot WHERE id = NEW.lot_id AND qty = 1
                ) THEN
                    RAISE EXCEPTION 'A tool lot must reference a lot with qty = 1';
                END IF;
            ELSE
                IF EXISTS (
                    SELECT 1 FROM tool_lot WHERE lot_id = NEW.id
                ) AND NEW.qty <> 1 THEN
                    RAISE EXCEPTION 'A lot referenced by tool_lot must have qty = 1';
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE TRIGGER enforce_tool_lot_quantity_on_insert
        BEFORE INSERT OR UPDATE ON tool_lot
        FOR EACH ROW EXECUTE FUNCTION enforce_tool_lot_single_quantity();
        """
    )
    op.execute(
        """
        CREATE TRIGGER enforce_tool_lot_quantity_on_lot_update
        BEFORE UPDATE OF qty ON lot
        FOR EACH ROW EXECUTE FUNCTION enforce_tool_lot_single_quantity();
        """
    )
    op.execute(
        """
        CREATE FUNCTION enforce_default_tool_lot()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        DECLARE
            owner_id uuid;
            tool_category text;
        BEGIN
            IF NOT NEW.is_default THEN
                RETURN NEW;
            END IF;

            EXECUTE $query$
                SELECT l.user_id,
                       CASE
                           WHEN EXISTS (SELECT 1 FROM finder f WHERE f.item_id = sl.item_id)
                               THEN 'finder'
                           WHEN EXISTS (SELECT 1 FROM excavator e WHERE e.item_id = sl.item_id)
                               THEN 'excavator'
                           WHEN EXISTS (SELECT 1 FROM refiner r WHERE r.item_id = sl.item_id)
                               THEN 'refiner'
                       END
                FROM lot l
                JOIN session_line sl ON sl.id::text = l.origin_id
                WHERE l.id = $1
            $query$ INTO owner_id, tool_category USING NEW.lot_id;

            IF tool_category IS NULL THEN
                RAISE EXCEPTION
                    'Only finder, excavator, or refiner lots can be default';
            END IF;

            PERFORM pg_advisory_xact_lock(
                hashtextextended(owner_id::text || ':' || tool_category, 0)
            );

            EXECUTE $query$
                UPDATE tool_lot tl
                SET is_default = false
                FROM lot l
                JOIN session_line sl ON sl.id::text = l.origin_id
                WHERE tl.lot_id = l.id
                  AND l.user_id = $1
                  AND tl.lot_id <> $3
                  AND tl.is_default
                  AND (
                      ($2 = 'finder' AND EXISTS
                          (SELECT 1 FROM finder f WHERE f.item_id = sl.item_id))
                      OR ($2 = 'excavator' AND EXISTS
                          (SELECT 1 FROM excavator e WHERE e.item_id = sl.item_id))
                      OR ($2 = 'refiner' AND EXISTS
                          (SELECT 1 FROM refiner r WHERE r.item_id = sl.item_id))
                  )
            $query$ USING owner_id, tool_category, NEW.lot_id;
            RETURN NEW;
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE TRIGGER enforce_default_tool_lot_trigger
        BEFORE INSERT OR UPDATE OF is_default ON tool_lot
        FOR EACH ROW EXECUTE FUNCTION enforce_default_tool_lot();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS enforce_default_tool_lot_trigger ON tool_lot")
    op.execute("DROP FUNCTION IF EXISTS enforce_default_tool_lot()")
    op.execute(
        "DROP TRIGGER IF EXISTS enforce_tool_lot_quantity_on_lot_update ON lot"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS enforce_tool_lot_quantity_on_insert ON tool_lot"
    )
    op.execute("DROP FUNCTION IF EXISTS enforce_tool_lot_single_quantity()")
    for table_name in ("enhancer_lot", "tool_lot", "material_lot"):
        op.drop_table(table_name)
    op.drop_table("lot")
    sa.Enum(name="lot_type").drop(op.get_bind(), checkfirst=True)
