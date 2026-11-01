"""create mining loot and planet relation tables"""

import sqlalchemy as sa
from alembic import op

revision = "018_create_mining_loot"
down_revision = "017_create_planet"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create mining loot and its many-to-many relation with planets."""

    mining_loot_type = sa.Enum("E", "O", "OE", name="mining_loot_type")
    op.create_table(
        "mining_loot",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("type", mining_loot_type, nullable=False),
        sa.Column("resource_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.Date(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "mining_loot_planet",
        sa.Column("planet_id", sa.Uuid(), nullable=False),
        sa.Column("mining_loot_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["planet_id"], ["planet.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["mining_loot_id"], ["mining_loot.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("planet_id", "mining_loot_id"),
    )


def downgrade() -> None:
    """Drop the mining loot relation, table, and enum."""

    op.drop_table("mining_loot_planet")
    op.drop_table("mining_loot")
    sa.Enum(name="mining_loot_type").drop(op.get_bind(), checkfirst=True)
