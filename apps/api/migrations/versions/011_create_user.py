"""create user table for cookie authentication"""

import sqlalchemy as sa
from alembic import op

revision = "011_create_user"
down_revision = "010_create_refiner"
branch_labels = None
depends_on = None


def upgrade() -> None:
    role = sa.Enum("USER", "ADMIN", name="user_role", create_type=False)
    role.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "user",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("pseudo", sa.String(length=50), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", role, server_default=sa.text("'USER'"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pseudo"),
    )


def downgrade() -> None:
    op.drop_table("user")
    sa.Enum(name="user_role").drop(op.get_bind(), checkfirst=True)
