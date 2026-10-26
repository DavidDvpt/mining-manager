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
        "TRADE",
        "CRAFTING",
        name="lot_and_session_type",
    )
    op.create_table(
        "lot",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("type", lot_and_session_type, nullable=False),
        sa.Column("origin_id", sa.String(), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
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


def downgrade() -> None:
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
    sa.Enum(name="lot_and_session_type").drop(op.get_bind(), checkfirst=True)
