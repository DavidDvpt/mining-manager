"""create claims table"""

import sqlalchemy as sa
from alembic import op

revision = "016_create_claims"
down_revision = "015_create_session"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "claims",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("item_id", sa.Uuid(), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column(
            "is_hof",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "depth",
            sa.Numeric(precision=5, scale=1),
            nullable=True,
        ),
        sa.Column("latitude", sa.Integer(), nullable=True),
        sa.Column("longitude", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.Date(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.Date(), nullable=True),
        sa.Column(
            "depleted",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["session_id"], ["session_mining.session_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["item_id"], ["item.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("claims")
