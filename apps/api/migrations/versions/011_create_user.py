"""create user table for cookie authentication"""

import sqlalchemy as sa
from alembic import op

revision = "011_create_user"
down_revision = "010_create_refiner"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the user table and seed the default application user."""

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
    user_table = sa.table(
        "user",
        sa.column("id", sa.Uuid()),
        sa.column("pseudo", sa.String(length=50)),
        sa.column("password_hash", sa.Text()),
        sa.column("role", role),
        sa.column("is_active", sa.Boolean()),
    )
    op.bulk_insert(
        user_table,
        [
            {
                "id": "e0c9a10f-ca78-4283-aa20-7eaebfcf09d2",
                "pseudo": "useruser",
                "password_hash": (
                    "$argon2id$v=19$m=65536,t=3,p=4$"
                    "mM3dVjj1quWygwiB57TaKQ$C3Xs/h9jH1rA3566xIouavAQEhbxNALwWhHQDO5Iv2o"
                ),
                "role": "USER",
                "is_active": True,
            }
        ],
    )


def downgrade() -> None:
    """Remove the user table and its PostgreSQL role enum."""

    op.drop_table("user")
    sa.Enum(name="user_role").drop(op.get_bind(), checkfirst=True)
