"""create profile table for user personal data"""

import sqlalchemy as sa
from alembic import op

revision = "012_create_profile"
down_revision = "011_create_user"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "profile",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("firstname", sa.String(length=100), nullable=True),
        sa.Column("lastname", sa.String(length=100), nullable=True),
        sa.Column("avatar_name", sa.String(length=100), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("email"),
    )


def downgrade() -> None:
    op.drop_table("profile")
