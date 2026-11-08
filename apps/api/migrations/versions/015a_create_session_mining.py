"""Create mining-specific session data."""

import sqlalchemy as sa
from alembic import op

revision = "015a_create_session_mining"
down_revision = "015_create_session"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create mining session configuration linked to a generic session."""

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
        "session_mining",
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("session_zone_id", sa.Uuid(), nullable=True),
        sa.Column("search_type", session_mining_search_type, nullable=False),
        sa.Column("clic", sa.Integer(), nullable=False),
        sa.CheckConstraint("clic > 0", name="ck_session_mining_clic_positive"),
        sa.ForeignKeyConstraint(
            ["session_id"], ["session.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("session_id"),
    )
    op.execute(
        """
        CREATE FUNCTION enforce_session_mining_immutability()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            RAISE EXCEPTION 'Mining session data is immutable';
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE TRIGGER enforce_session_mining_immutability_trigger
        BEFORE UPDATE ON session_mining
        FOR EACH ROW EXECUTE FUNCTION enforce_session_mining_immutability();
        """
    )


def downgrade() -> None:
    """Drop mining-specific session data."""

    op.execute(
        """
        DROP TRIGGER IF EXISTS enforce_session_mining_immutability_trigger
        ON session_mining
        """
    )
    op.execute("DROP FUNCTION IF EXISTS enforce_session_mining_immutability()")
    op.drop_table("session_mining")
    sa.Enum(name="session_mining_search_type").drop(
        op.get_bind(), checkfirst=True
    )
