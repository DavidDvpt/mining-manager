"""create session zone table"""

import sqlalchemy as sa
from alembic import op

revision = "019_create_session_zone"
down_revision = "018_create_mining_loot"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create named session zones linked to planets."""

    op.create_table(
        "session_zone",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("planete_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.Date(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["planete_id"], ["planet.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_foreign_key(
        "fk_session_mining_session_zone_id_session_zone",
        "session_mining",
        "session_zone",
        ["session_zone_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Drop the session zone table."""

    op.execute(
        """
        ALTER TABLE session_mining
        DROP CONSTRAINT IF EXISTS fk_session_mining_session_zone_id_session_zone,
        DROP CONSTRAINT IF EXISTS fk_session_mining_session_sone_id_session_zone
        """
    )
    op.drop_table("session_zone")
