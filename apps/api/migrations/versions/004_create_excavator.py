"""add excavators and efficiency details

Revision ID: 004_create_excavator
Revises: 003_create_finder
Create Date: 2026-10-22
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

import sqlalchemy as sa
from alembic import op

revision = "004_create_excavator"
down_revision = "003_create_finder"
branch_labels = None
depends_on = None


def _timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


EXCAVATORS = [
    ("b9699e57-6715-43e5-82e3-e4031993b97c", "ARD Excavator M1 (L)", None, "/excavators/3", 19, Decimal("6.8"), None, False, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.633Z"), Decimal("1.8"), Decimal("2.4"), Decimal("0.003")),
    ("7915a19d-fbbb-4f0c-a3a8-e1ab349426d7", "ARD Excavator M2 (L)", None, "/excavators/4", 24, Decimal("9.2"), None, False, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.636Z"), Decimal("1.6"), Decimal("54"), Decimal("0.01263")),
    ("49a244ab-7df9-49b5-8dea-f84e672ccf2a", "ARD Excavator M5 (L)", None, "/excavators/7", 26, Decimal("12.8"), None, False, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.637Z"), Decimal("1.9"), Decimal("132"), Decimal("0.02336")),
    ("1feba321-db21-4faf-b9b5-126a55c424d2", "Demonic Excavator MK-I (L)", None, "/excavators/8", 17, Decimal("0.6"), None, False, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.638Z"), Decimal("1"), Decimal("5"), Decimal("0.001")),
    ("e8cc6f11-9136-4e40-b418-4d935f29b2f0", "Earth Excavator ME/01", 409, "/excavators/9", 19, Decimal("6.8"), None, False, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.639Z"), Decimal("2"), Decimal("2.4"), Decimal("0.003")),
    ("93a0563d-1377-42cb-9204-b1bed4e577a9", "eMINE E (L)", 3043, "/excavators/10", 27, Decimal("12"), None, False, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.640Z"), Decimal("1.5"), Decimal("85"), Decimal("0.02101")),
    ("3d28f0ee-d190-4f06-9ef1-988b1333b52e", "Genesis Star Basic Excavator (L)", 409, "/excavators/13", 19, Decimal("6.8"), None, False, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.641Z"), Decimal("2"), Decimal("3"), Decimal("0.003")),
    ("5150d2f5-42d5-44d3-aebd-7aac511a8101", "Genesis Star Earth Excavator ME/02", 409, "/excavators/14", 22, Decimal("7.2"), None, False, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.642Z"), Decimal("2"), Decimal("8"), Decimal("0.005")),
    ("a4fa77c6-f1b1-4a06-9206-b4f0d2329985", "Genesis Star Earth Excavator ME/05", 409, "/excavators/17", 23, Decimal("8.8"), None, False, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.643Z"), Decimal("1"), Decimal("66"), Decimal("0.008")),
    ("c806425b-4b0a-46ad-bcaa-586e0dd2c732", "Imperium Extirpater v1", 5641, "/excavators/26", 19, Decimal("6.8"), None, False, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.650Z"), Decimal("1"), Decimal("2.2"), Decimal("0.0034")),
    ("d1b26a69-593d-4ae8-9994-3cd91d519ee5", "Island Earth Excavator ME/01", 409, "/excavators/28", 19, Decimal("6.8"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.651Z"), Decimal("2"), Decimal("2.4"), Decimal("0.003")),
    ("a73b8134-81fe-4f36-ba54-92f75354b141", "Punk Digger (L)", 410, "/excavators/32", 19, Decimal("6.8"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.652Z"), Decimal("2"), Decimal("3"), Decimal("0.003")),
    ("b7e89733-6c59-4e33-83c8-28f4cbcdef49", "Genesis Star Excavator, Adjusted", 409, "/excavators/19", 23, Decimal("12.8"), None, True, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.646Z"), Decimal("2"), Decimal("18"), Decimal("0.005")),
    ("a7095f2e-afd6-4c24-bb58-e147e95a82a1", "Genesis Star Excavator, Adjusted, TWEN Edition", 409, "/excavators/20", 23, Decimal("16.8"), None, True, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.646Z"), Decimal("1"), Decimal("100"), Decimal("0.005")),
    ("741640c9-61be-4886-8708-a6372e81aa93", "Genesis Star Excavator, Improved, TWEN Edition", 409, "/excavators/22", 24, Decimal("19.2"), None, True, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.647Z"), Decimal("1"), Decimal("200"), Decimal("0.005")),
    ("898281fb-d3b0-44b7-8dc7-bb764e2fc466", "Genesis Star Excavator, Modified", 409, "/excavators/23", 27, Decimal("20.8"), None, True, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.648Z"), Decimal("0.8"), Decimal("4362"), Decimal("0.03212")),
    ("56f10649-7e69-4b67-8abd-251f590067a2", "Genesis Star Excavator, Modified, TWEN Edition", None, "/excavators/24", 27, Decimal("24.8"), None, True, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.649Z"), Decimal("0.8"), Decimal("400"), Decimal("0.03212")),
    ("9faa3434-9fe8-4a70-aeb0-c798a89b177f", "Resource Extractor RE-101", 407, "/excavators/33", 20, Decimal("7.2"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.653Z"), Decimal("2"), Decimal("5.5"), Decimal("0.006")),
    ("97beefbf-8952-4a6a-b256-0f2fea5e935c", "Resource Extractor RE-204 (L)", 407, "/excavators/41", 26, Decimal("12.8"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.653Z"), Decimal("1.5"), Decimal("195"), Decimal("0.02331")),
    ("33f8d4dd-504b-4856-a6d1-613f50543b24", "Resource Extractor RE-204 Adapted (L)", None, "/excavators/42", 34, Decimal("12.8"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.654Z"), Decimal("1.5"), Decimal("195"), Decimal("0.02331")),
    ("7fcb710d-646a-43a0-84ba-bf8ef5223cb0", "Resource Extractor RE-301 (L)", 407, "/excavators/44", 24, Decimal("14"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.655Z"), Decimal("3.9"), Decimal("83"), Decimal("0.02503")),
    ("4cb9403d-3fad-444b-a433-65613a87527a", "Rock Ripper 1 (L)", 4703, "/excavators/45", 22, Decimal("6.6"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.656Z"), Decimal("1.4"), Decimal("2"), Decimal("0.0028")),
    ("7a91dc10-8882-4cc7-bb89-73b3dc9bb3e0", "Rock Ripper 2 (L)", 4703, "/excavators/46", 24, Decimal("7.7"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.656Z"), Decimal("1.4"), Decimal("22"), Decimal("0.01129")),
    ("061a82b8-7725-44cc-bbdc-adcb7f856162", "Rock Ripper 3 (L)", 4703, "/excavators/47", 24, Decimal("8.8"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.657Z"), Decimal("1.4"), Decimal("44"), Decimal("0.01454")),
    ("bb279986-59d8-41c2-b6fb-bdff6649494a", "Rock Ripper Trainer (L)", 4703, "/excavators/50", 17, Decimal("6"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.659Z"), Decimal("1.4"), Decimal("0.2"), Decimal("0.00274")),
    ("510959f7-dc56-4a1d-86fc-83814f1a6861", "Rock Ripper TT (L)", None, "/excavators/51", 19, Decimal("6.8"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.660Z"), Decimal("2"), Decimal("3"), Decimal("0.003")),
    ("f0806671-9997-408a-98a1-ca2e1995a88a", "Exhumer Mk1", None, "/excavators/11", 19, Decimal("6.8"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.663Z"), Decimal("2"), Decimal("2.4"), Decimal("0.003")),
    ("0a3dbc08-9089-4cfd-bcbd-ffbc9757760e", "ARD Excavator A-100 (L)", None, "/excavators/1", 19, Decimal("6.8"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.664Z"), Decimal("2"), Decimal("3"), Decimal("0.003")),
    ("01e99bef-805e-44ae-80a2-bd86367f1dd6", "ARD Excavator Beginner (L)", None, "/excavators/2", 17, Decimal("1.2"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.665Z"), Decimal("1.4"), Decimal("0.05"), Decimal("0.0031")),
    ("2682040e-463b-4a6c-a480-8c9214219e4c", "Genesis Rookie Extractor (L)", None, "/excavators/12", 17, Decimal("1.2"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.666Z"), Decimal("1.5"), Decimal("0.01"), Decimal("0.00313")),
    ("c4c4f505-bba2-4f66-acb2-e8bcd1fa66d4", "Genesis Star Earth Excavator ME/04", 409, "/excavators/16", 23, Decimal("8"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.667Z"), Decimal("1"), Decimal("55"), Decimal("0.0083")),
    ("bc7d4f41-0a22-4e97-b8ff-5d07419ce602", "Genesis Star Rookie Extractor (L)", 409, "/excavators/25", 17, Decimal("1.2"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.667Z"), Decimal("1.5"), Decimal("0.1"), Decimal("0.001")),
    ("22a0fdd6-ab74-47de-a4ff-683a0ecaa4a3", "Initiate's Excavator (L)", 5641, "/excavators/27", 19, Decimal("6.8"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.668Z"), Decimal("2"), Decimal("3"), Decimal("0.003")),
    ("7637bfa6-741f-4a44-995c-b70f70adabee", "Lost Soul Savior (L)", 410, "/excavators/29", 26, Decimal("19.2"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.669Z"), Decimal("2.4"), Decimal("64"), Decimal("0.012")),
    ("f35d5055-5b07-42e7-9aee-fd45c92af0bf", "NI Basic Excavator (L)", 409, "/excavators/30", 19, Decimal("6.8"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.670Z"), Decimal("2"), Decimal("3"), Decimal("0.003")),
    ("bb604dce-afd2-4579-885a-2e8ff88fa387", "Resource Extractor RE-103", 407, "/excavators/35", 23, Decimal("8.4"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.671Z"), Decimal("2"), Decimal("50"), Decimal("0.016")),
    ("f0e9dc3b-bd9e-4168-85ac-dda7f8d4d6ff", "Resource Extractor RE-104", 407, "/excavators/36", 24, Decimal("9.6"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.671Z"), Decimal("1.5"), Decimal("65"), Decimal("0.0172")),
    ("08fcda30-fffd-4b64-92ff-152cf6cfe425", "Resource Extractor RE-105", 407, "/excavators/37", 26, Decimal("10.8"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.672Z"), Decimal("1.3"), Decimal("80"), Decimal("0.02215")),
    ("a363288e-9a6b-4f53-8bc5-1e89360fe03b", "Genesis Star Excavator, Improved", 409, "/excavators/21", 24, Decimal("15.2"), None, True, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.663Z"), Decimal("2"), Decimal("27"), Decimal("0.005")),
    ("5c296658-684f-4c11-91a2-3a6ccc0dcbe9", "Resource Extractor RE-201 (L)", 407, "/excavators/38", 25, Decimal("9.2"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.673Z"), Decimal("1.7"), Decimal("89"), Decimal("0.01263")),
    ("f261837d-b4b7-43f9-9ceb-3e8dbe49f6fc", "Resource Extractor RE-202 (L)", 407, "/excavators/39", 25, Decimal("10.4"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.674Z"), Decimal("1.5"), Decimal("110"), Decimal("0.01614")),
    ("68eb70ed-23ba-4d37-8344-f65945a3244c", "Rock Ripper 4 (L)", 4703, "/excavators/49", None, None, None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.679Z"), Decimal("1.4"), Decimal("70"), Decimal("0.01732")),
    ("6e1643f1-60e4-481d-99dc-b92f394a3060", "Genesis Star Earth Excavator ME/05, SGA Edition", None, "/excavators/18", 33, Decimal("8.8"), None, True, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.644Z"), Decimal("1"), Decimal("66"), Decimal("0.008")),
    ("d0c7bfea-0a6f-4ba4-b4c2-bf62bd5e1d6a", "Rock Ripper 3 Gold Rush", None, "/excavators/48", 29, Decimal("8.5"), None, True, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.658Z"), Decimal("1.4"), Decimal("44"), Decimal("0.00833")),
    ("5e477405-2e90-4c24-8d35-d5ec47acc67b", "Resource Extractor RE-203 (L)", 407, "/excavators/40", 25, Decimal("11.6"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.674Z"), Decimal("1.5"), Decimal("185"), Decimal("0.02065")),
    ("8dc021db-5fd3-4223-88ef-ea310de78539", "Resource Extractor RE-205 (L)", None, "/excavators/43", 24, Decimal("14"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.675Z"), Decimal("3.9"), Decimal("83"), Decimal("0.02503")),
    ("ea3c2573-5fe8-41cb-afd3-97c9f4a9f342", "Training Mineral Extractor (L)", 5641, "/excavators/53", 19, Decimal("6.8"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.676Z"), Decimal("1"), Decimal("0.1"), Decimal("0.0034")),
    ("d777327f-695b-4d0f-b0a1-9f311c10601b", "Genesis Star Earth Excavator ME/03", 409, "/excavators/15", 22, Decimal("7.2"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.676Z"), Decimal("2"), Decimal("42"), Decimal("0.0086")),
    ("12502c58-6a33-485e-8c3d-36a126d0125f", "Resource Extractor RE-102", 407, "/excavators/34", 22, Decimal("8"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.677Z"), Decimal("2"), Decimal("15"), Decimal("0.0115")),
    ("eca026be-2469-4e38-8006-d143e1c3ceed", "ARD Excavator M3 (L)", None, "/excavators/5", None, None, None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.678Z"), Decimal("1.75"), Decimal("72"), Decimal("0.01614")),
    ("9501cbd1-0e81-4fb2-bafe-d507aea0180a", "ARD Excavator M4 (L)", None, "/excavators/6", None, None, None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.678Z"), Decimal("1.9"), Decimal("98"), Decimal("0.02068")),
    ("2a36169a-9582-4d3f-b5fa-1222c99e5283", "Rookie Rock Ripper", 5679, "/excavators/52", 17, Decimal("6"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.660Z"), Decimal("1.4"), Decimal("1"), Decimal("0.00274")),
    ("99096eea-9927-4fcc-bd29-e7f97d4ad38f", "Xtreme Excavator MK-I (L)", 410, "/excavators/54", 17, Decimal("7.6"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.661Z"), Decimal("1"), Decimal("5"), Decimal("0")),
    ("e3281c88-645b-4e30-af1a-d5862ccd14ba", "NI Extractor New Settler Issue (L)", 409, "/excavators/31", 24, Decimal("1.2"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.662Z"), Decimal("2"), Decimal("0.1"), Decimal("0.001")),
]


def upgrade() -> None:
    op.create_table(
        "excavator",
        sa.Column("item_id", sa.Uuid(), nullable=False),
        sa.Column("use_per_minute", sa.Integer(), nullable=True),
        sa.Column("efficiency", sa.Numeric(), nullable=True),
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
    excavator_table = sa.table(
        "excavator",
        sa.column("item_id", sa.Uuid()),
        sa.column("use_per_minute", sa.Integer()),
        sa.column("efficiency", sa.Numeric()),
    )
    economy_table = sa.table(
        "economy",
        sa.column("item_id", sa.Uuid()),
        sa.column("tt", sa.Numeric()),
        sa.column("decay", sa.Numeric()),
    )

    op.bulk_insert(
        item_table,
        [
            {
                "id": UUID(row[0]),
                "name": row[1],
                "img_id": row[2],
                "weight": row[11],
                "is_active": True,
                "nexus_url": row[3],
                "description": row[6],
                "is_rare": row[7],
                "is_untradeable": row[8],
                "created_at": row[9],
                "updated_at": row[10],
            }
            for row in EXCAVATORS
        ],
    )
    op.bulk_insert(
        excavator_table,
        [
            {
                "item_id": UUID(row[0]),
                "use_per_minute": row[4],
                "efficiency": row[5],
            }
            for row in EXCAVATORS
        ],
    )
    op.bulk_insert(
        economy_table,
        [
            {
                "item_id": UUID(row[0]),
                "tt": row[12],
                "decay": row[13],
            }
            for row in EXCAVATORS
        ],
    )


def downgrade() -> None:
    bind = op.get_bind()
    item_ids = [UUID(row[0]) for row in EXCAVATORS]

    economy_table = sa.table("economy", sa.column("item_id", sa.Uuid()))
    excavator_table = sa.table("excavator", sa.column("item_id", sa.Uuid()))
    item_table = sa.table("item", sa.column("id", sa.Uuid()))
    bind.execute(economy_table.delete().where(economy_table.c.item_id.in_(item_ids)))
    bind.execute(excavator_table.delete().where(excavator_table.c.item_id.in_(item_ids)))
    bind.execute(item_table.delete().where(item_table.c.id.in_(item_ids)))
    op.drop_table("excavator")
