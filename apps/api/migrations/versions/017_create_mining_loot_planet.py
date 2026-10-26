"""create mining loot, planet, and their relation"""

import sqlalchemy as sa
from alembic import op

revision = "017_create_mining_loot_planet"
down_revision = "016_create_claims"
branch_labels = None
depends_on = None


def upgrade() -> None:
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "planet",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
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
    op.drop_table("mining_loot_planet")
    op.drop_table("planet")
    op.drop_table("mining_loot")
    sa.Enum(name="mining_loot_type").drop(op.get_bind(), checkfirst=True)
