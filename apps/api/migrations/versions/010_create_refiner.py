"""create refiner table and seed refiners

Revision ID: 010_create_refiner
Revises: 009_create_material
Create Date: 2026-10-25
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

import sqlalchemy as sa
from alembic import op

revision = "010_create_refiner"
down_revision = "009_create_material"
branch_labels = None
depends_on = None


def _timestamp(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _decimal_5(value: str) -> Decimal:
    return Decimal(value).quantize(Decimal("0.00001"))


REFINERS = [
    ("a3c66e29-9d2a-4668-8e53-258a7b3fee11", "Apprentice Refiner AR-1 (L)", None, "0.10000", "0.00001", "2026-10-12T14:32:07.997Z", False, False, "2.20000", "/refiners/26"),
    ("38a46660-086d-4d13-8082-876f174f7720", "Chikara Refiner, Adjusted", 7033, "24", "0.00015", "2026-10-12T14:32:07.997Z", False, False, "6", "/refiners/1"),
    ("2fc99a19-e87f-4c25-913d-455e738dd21f", "Chikara Refiner, Modified", 7033, "41", "0.00013", "2026-10-12T14:32:07.997Z", False, False, "6", "/refiners/2"),
    ("98a67f31-5ec2-45a9-979a-b3ec67eb8a88", "Chikara Refiner MR200", 7033, "16", "0.00023", "2026-10-12T14:32:07.997Z", False, False, "6", "/refiners/3"),
    ("da3f2d33-7770-4897-af49-7d2888a4c400", "Chikara Refiner MR300", 7033, "35", "0.00022", "2026-10-12T14:32:07.997Z", False, False, "6", "/refiners/4"),
    ("3184ed7c-449d-452c-aa23-9610a9ee91c5", "Chikara Refiner MR400", 7033, "48", "0.00020", "2026-10-12T14:32:07.997Z", False, False, "5", "/refiners/5"),
    ("5cd1b1f3-b737-42a4-8ced-cc3b47897efe", "Demonic Refiner MK-I (L)", 7032, "2", "0.00030", "2026-10-12T14:32:07.997Z", False, False, "6", "/refiners/6"),
    ("53ec5c29-26b2-4923-ab10-935d12834d72", "Genesis Rookie OreRefiner (L)", 7033, "0.01000", "0.00110", "2026-10-12T14:32:07.997Z", False, False, "4", "/refiners/7"),
    ("eafb901a-d851-423b-a2ec-13f580f89a80", "Genesis Star Basic Refiner", 7033, "2", "0.00031", "2026-10-12T14:32:07.997Z", False, False, "6", "/refiners/8"),
    ("5376ee27-6777-4309-9d6c-5eaff6fb8edf", "Imperium Resource Refiner 1A", 7031, "3", "0.00030", "2026-10-12T14:32:07.997Z", False, False, "6", "/refiners/9"),
    ("56ad2496-a764-4b08-ae63-474a57330e88", "Imperium Resource Refiner B1", 7031, "6", "0.00022", "2026-10-12T14:32:07.997Z", False, False, "6", "/refiners/10"),
    ("dcb6fc43-4297-490b-a3af-fb04516de1d6", "Initiate's Refiner", 7031, "2", "0.00031", "2026-10-12T14:32:07.997Z", False, False, "6", "/refiners/11"),
    ("ad97231f-e26a-4c5c-8c6a-c729708089e9", "NI Basic Refiner", 7033, "2", "0.00031", "2026-10-12T14:32:07.997Z", False, False, "6", "/refiners/12"),
    ("64822d75-19fb-420d-ad2f-6ae6de3e27fe", "NI Refiner New Settler Issue", 7033, "1", "0.00031", "2026-10-12T14:32:07.997Z", False, False, "6", "/refiners/13"),
    ("f70378fc-9b17-4062-9944-535f78e54fdd", "OreTransformer OT-101", None, "8", "0.00030", "2026-10-12T14:32:07.997Z", False, False, "5", "/refiners/23"),
    ("523741c1-06a9-4c6f-aa87-238dd9cd7bd5", "OreTransformer OT-102", None, "22", "0.00028", "2026-10-12T14:32:07.997Z", False, False, "5", "/refiners/24"),
    ("f7f474bc-533d-4cb0-bdd4-03a4f975216e", "OreTransformer OT-103", None, "45", "0.00026", "2026-10-12T14:32:07.997Z", False, False, "5", "/refiners/25"),
    ("fff788d9-76c8-4d78-a572-bb3823fdd253", "PTech Refiner 1", 4848, "2", "0.00030", "2026-10-12T14:32:07.997Z", False, False, "3", "/refiners/14"),
    ("0c191264-4a93-4910-b2d0-ac54685ec975", "PTech Refiner TT", 4848, "2", "0.00031", "2026-10-12T14:32:07.997Z", False, False, "6", "/refiners/15"),
    ("0bd0e1c7-9494-42ec-9a9e-4fd3a4a98904", "Punk Blender", 7033, "2", "0.00031", "2026-10-12T14:32:07.997Z", False, False, "6", "/refiners/16"),
    ("3117a32a-3909-424c-a4e3-1d3bea553c00", "Refiner MR100", 7033, "2", "0.00031", "2026-10-12T14:32:07.997Z", False, False, "6", "/refiners/17"),
    ("55975307-5aed-456a-9785-e68d1614562c", "Transformer T-101", 7033, "8", "0.00030", "2026-10-12T14:32:07.997Z", False, False, "5", "/refiners/18"),
    ("5c063e4c-6f9d-4fb4-a6fd-0048ae9cb4c7", "Transformer T-102", 7033, "22.75", "0.00028", "2026-10-12T14:32:07.997Z", False, False, "5", "/refiners/19"),
    ("1a7c62a9-339b-427f-b97e-abe252ee5cdb", "Transformer T-103", 7033, "45.5", "0.00026", "2026-10-12T14:32:07.997Z", False, False, "4.5", "/refiners/20"),
    ("7492e25f-2d99-40ed-b9fa-31f6d8a6debc", "Transformer T-104", 7033, "55.30000", "0.00023", "2026-10-12T14:32:07.997Z", False, False, "4", "/refiners/21"),
    ("fe64d6b8-826c-452a-9f59-6d92fe2e4613", "Transformer T-105", 7033, "75", "0.00021", "2026-10-12T14:32:07.997Z", False, False, "4", "/refiners/22"),
]


def upgrade() -> None:
    op.create_table(
        "refiner",
        sa.Column("item_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["item_id"], ["item.id"]),
        sa.PrimaryKeyConstraint("item_id"),
    )

    item_table = sa.table(
        "item",
        sa.column("id", sa.Uuid()),
        sa.column("name", sa.String()),
        sa.column("img_id", sa.Integer()),
        sa.column("weight", sa.Numeric()),
        sa.column("is_active", sa.Boolean()),
        sa.column("nexus_url", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("is_rare", sa.Boolean()),
        sa.column("is_untradeable", sa.Boolean()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    refiner_table = sa.table(
        "refiner",
        sa.column("item_id", sa.Uuid()),
    )
    economy_table = sa.table(
        "economy",
        sa.column("item_id", sa.Uuid()),
        sa.column("tt", sa.Numeric(precision=20, scale=5)),
        sa.column("decay", sa.Numeric(precision=20, scale=5)),
    )

    op.bulk_insert(
        item_table,
        [
            {
                "id": UUID(row[0]),
                "name": row[1],
                "img_id": row[2],
                "weight": Decimal(row[8]),
                "is_active": True,
                "nexus_url": row[9],
                "description": None,
                "is_rare": row[6],
                "is_untradeable": row[7],
                "created_at": _timestamp(row[5]),
                "updated_at": None,
            }
            for row in REFINERS
        ],
    )
    op.bulk_insert(
        refiner_table,
        [{"item_id": UUID(row[0])} for row in REFINERS],
    )
    op.bulk_insert(
        economy_table,
        [
            {
                "item_id": UUID(row[0]),
                "tt": _decimal_5(row[3]),
                "decay": _decimal_5(row[4]),
            }
            for row in REFINERS
        ],
    )


def downgrade() -> None:
    bind = op.get_bind()
    item_ids = [UUID(row[0]) for row in REFINERS]

    economy_table = sa.table("economy", sa.column("item_id", sa.Uuid()))
    refiner_table = sa.table("refiner", sa.column("item_id", sa.Uuid()))
    item_table = sa.table("item", sa.column("id", sa.Uuid()))
    bind.execute(economy_table.delete().where(economy_table.c.item_id.in_(item_ids)))
    bind.execute(refiner_table.delete().where(refiner_table.c.item_id.in_(item_ids)))
    bind.execute(item_table.delete().where(item_table.c.id.in_(item_ids)))
    op.drop_table("refiner")
