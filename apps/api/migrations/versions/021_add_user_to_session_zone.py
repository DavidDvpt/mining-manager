"""Associate session zones with their creating users."""

import sqlalchemy as sa
from alembic import op

revision = "021_add_user_to_session_zone"
down_revision = "020_create_refinage_recipe"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add the mandatory owner foreign key to session zones."""

    op.add_column(
        "session_zone",
        sa.Column("user_id", sa.Uuid(), nullable=False),
    )
    op.create_foreign_key(
        "fk_session_zone_user_id_user",
        "session_zone",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Remove the session-zone owner foreign key and column."""

    op.drop_constraint("fk_session_zone_user_id_user", "session_zone", type_="foreignkey")
    op.drop_column("session_zone", "user_id")
