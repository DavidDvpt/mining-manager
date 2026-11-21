"""create planet and session zone tables"""

import sqlalchemy as sa
from alembic import op

revision = "017_create_planet"
down_revision = "016_create_claims"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the planet catalogue and owned session-zone tables."""

    op.create_table(
        "planet",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("nexus_url", sa.String(), nullable=True),
        sa.Column("created_at", sa.Date(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
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
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.Date(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["planete_id"], ["planet.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], ondelete="CASCADE"
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
    """Drop the session-zone and planet tables."""

    op.drop_constraint(
        "fk_session_mining_session_zone_id_session_zone",
        "session_mining",
        type_="foreignkey",
    )
    op.drop_table("session_zone")
    op.drop_table("planet")
