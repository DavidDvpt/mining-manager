"""seed the initial planet catalogue"""

import sqlalchemy as sa
from alembic import op

revision = "019_create_session_zone"
down_revision = "018_create_mining_loot"
branch_labels = None
depends_on = None


PLANETS = [
    ("Entropia Universe", "/planets/0"),
    ("Calypso", "/planets/1"),
    ("Arkadia", "/planets/2"),
    ("Monria", "/planets/3"),
    ("ROCKtropia", "/planets/4"),
    ("Toulan", "/planets/5"),
    ("Next Island", "/planets/6"),
    ("Cyrene", "/planets/7"),
    ("DSEC9", "/planets/8"),
    ("Hunt The THING", "/planets/9"),
    ("Ancient Greece", "/planets/11"),
    ("Arkadia Underground", "/planets/12"),
    ("Arkadia Moon", "/planets/13"),
    ("Secret Island", "/planets/14"),
    ("Asteroid F.O.M.A.", "/planets/15"),
    ("Crystal Palace", "/planets/16"),
    ("Space", "/planets/17"),
    ("HELL", "/planets/18"),
    ("ARIS", "/planets/19"),
    ("Setesh", "/planets/20"),
    ("Howling Mine", "/planets/21"),
    ("The HUB", "/planets/24"),
]


def upgrade() -> None:
    """Insert the initial planet names and let PostgreSQL generate their UUIDs."""

    planet_table = sa.table(
        "planet",
        sa.column("name", sa.String()),
        sa.column("nexus_url", sa.String()),
    )
    op.bulk_insert(
        planet_table,
        [{"name": name, "nexus_url": url} for name, url in PLANETS],
    )


def downgrade() -> None:
    """Remove only the planets inserted by this seed migration."""

    planet_table = sa.table(
        "planet",
        sa.column("name", sa.String()),
    )
    op.execute(
        planet_table.delete().where(
            planet_table.c.name.in_([name for name, _ in PLANETS]),
        )
    )
