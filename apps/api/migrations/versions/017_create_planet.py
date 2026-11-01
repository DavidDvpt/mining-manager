"""create planet table"""

import sqlalchemy as sa
from alembic import op

revision = "017_create_planet"
down_revision = "016_create_claims"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the planet catalogue table."""

    op.create_table(
        "planet",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.Date(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Drop the planet table."""

    op.drop_table("planet")
