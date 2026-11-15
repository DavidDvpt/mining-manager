"""seed the initial planet catalogue"""

import sqlalchemy as sa
from alembic import op

revision = "022_seed_planets"
down_revision = "021_add_user_to_session_zone"
branch_labels = None
depends_on = None


PLANET_NAMES = [
    "Entropia Universe",
    "Calypso",
    "Arkadia",
    "Monria",
    "ROCKtropia",
    "Toulan",
    "Next Island",
    "Cyrene",
    "DSEC9",
    "Hunt The THING",
    "Ancient Greece",
    "Arkadia Underground",
    "Arkadia Moon",
    "Secret Island",
    "Asteroid F.O.M.A.",
    "Crystal Palace",
    "Space",
    "HELL",
    "Setesh",
    "Howling Mine",
    "ARIS",
    "The HUB",
]


def upgrade() -> None:
    """Insert the initial planet names and let PostgreSQL generate their UUIDs."""

    planet_table = sa.table(
        "planet",
        sa.column("name", sa.String()),
    )
    op.bulk_insert(
        planet_table,
        [{"name": name} for name in PLANET_NAMES],
    )


def downgrade() -> None:
    """Remove only the planets inserted by this seed migration."""

    planet_table = sa.table(
        "planet",
        sa.column("name", sa.String()),
    )
    op.execute(
        planet_table.delete().where(
            planet_table.c.name.in_(PLANET_NAMES),
        )
    )
