"""create enhancer table and seed enhancers

Revision ID: 006_create_enhancer
Revises: 005_create_finder_amplifier
Create Date: 2026-10-23
"""

import re
from datetime import datetime
from decimal import Decimal
from uuid import UUID

import sqlalchemy as sa
from alembic import op

revision = "006_create_enhancer"
down_revision = "005_create_finder_amplifier"
branch_labels = None
depends_on = None


def _timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value)


ENHANCERS = [
    ('7e600b91-2576-45d3-b866-18516feb952b', 'T1 Mining Finder Depth Enhancer', 3286, '/enhancers/101', None, False, False, _timestamp('2026-10-11T23:44:31.983Z'), None, Decimal('0.01'), Decimal('0.8'), None),
    ('5dcd209b-9b28-4875-8b20-0a70507071ec', 'T3 Mining Finder Depth Enhancer', 3317, '/enhancers/103', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.8'), None),
    ('b5171d31-84d1-4655-8ab7-7ce5d1c81c72', 'T4 Mining Finder Depth Enhancer', 3306, '/enhancers/104', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.8'), None),
    ('1724f40f-27da-4e40-8b17-8b3ffb53882b', 'T5 Mining Finder Depth Enhancer', 3341, '/enhancers/105', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.8'), None),
    ('0f8cf859-db9b-48e7-bc60-1a100a49d1da', 'T7 Mining Finder Depth Enhancer', 4112, '/enhancers/107', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.8'), None),
    ('22336307-b269-47dd-a1e0-e71003212e6b', 'T8 Mining Finder Depth Enhancer', 4114, '/enhancers/108', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal('0.8'), None),
    ('c0b83fab-a0c8-4a15-beb9-09b82c68f8e8', 'T10 Mining Finder Depth Enhancer', 4529, '/enhancers/110', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal('0.8'), None),
    ('954849ea-0d6d-4565-abc0-bb4befe066e9', 'T2 Mining Finder Range Enhancer', 3318, '/enhancers/112', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal(1), None),
    ('1b5555b2-2f3c-4136-9f72-d70d1fbbdf4a', 'T2 Mining Finder Depth Enhancer', 3305, '/enhancers/102', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.8'), None),
    ('f53512a7-2b43-44f3-8aee-5d0ac8952a8f', 'T1 Mining Finder Range Enhancer', 3283, '/enhancers/111', None, False, False, _timestamp('2026-10-11T23:44:31.983Z'), None, Decimal('0.01'), Decimal(1), None),
    ('1c09821c-a495-4539-a701-e9746029a69e', 'T1 Mining Finder Skill Modification Enhancer', 3256, '/enhancers/121', None, False, False, _timestamp('2026-10-11T23:44:31.983Z'), None, Decimal('0.01'), Decimal('0.6'), None),
    ('5e8dd11f-aae4-40d2-b4a0-34fab467fab8', 'T2 Mining Finder Skill Modification Enhancer', 3340, '/enhancers/122', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.6'), None),
    ('34724811-0d9f-407b-bb4d-043c11faeef8', 'T1 Mining Excavator Speed Enhancer', 3255, '/enhancers/131', None, False, False, _timestamp('2026-10-11T23:44:31.983Z'), None, Decimal('0.01'), Decimal('0.2'), None),
    ('f4a28c9f-fc4e-499d-8332-bae97a507a7d', 'T2 Mining Excavator Speed Enhancer', 3280, '/enhancers/132', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.2'), None),
    ('8cce77e7-995f-4da1-9500-d4ee2532049f', 'T3 Mining Finder Range Enhancer', 3319, '/enhancers/113', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal(1), None),
    ('58015179-fdb9-4324-bbe8-1ce839754976', 'T3 Mining Finder Skill Modification Enhancer', 3269, '/enhancers/123', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.6'), None),
    ('35ddc91c-30de-4887-bcdd-23c29c9c47fd', 'T3 Mining Excavator Speed Enhancer', 3281, '/enhancers/133', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.2'), None),
    ('45a0cced-b55a-485b-ad07-eb4fd019fe63', 'T4 Mining Finder Range Enhancer', 3320, '/enhancers/114', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal(1), None),
    ('9e699cc8-0101-41db-8ac6-7a16e449310e', 'T4 Mining Finder Skill Modification Enhancer', 4375, '/enhancers/124', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.6'), None),
    ('cc42f9c9-d1bd-4bf3-86d4-9d0b3952fc5a', 'T4 Mining Excavator Speed Enhancer', 3282, '/enhancers/134', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.2'), None),
    ('ea69a31d-1349-47f2-a578-551225221184', 'T6 Mining Finder Depth Enhancer', 4113, '/enhancers/106', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.8'), None),
    ('f903e562-d577-48fb-a490-ccc779fde85c', 'T5 Mining Finder Range Enhancer', 3321, '/enhancers/115', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal(1), None),
    ('da181d6d-7d65-4cdd-b679-1784745a4bde', 'T6 Mining Finder Range Enhancer', 3339, '/enhancers/116', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal(1), None),
    ('a844d9e8-fcf1-4a32-87ce-e6c6091e7901', 'T5 Mining Finder Skill Modification Enhancer', 3308, '/enhancers/125', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.6'), None),
    ('e9c876e0-524a-4b10-8a5f-cb687a62bc9b', 'T6 Mining Finder Skill Modification Enhancer', 4525, '/enhancers/126', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.6'), None),
    ('f1b0ed62-500e-4c79-aa23-066be64ddd81', 'T5 Mining Excavator Speed Enhancer', 3338, '/enhancers/135', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.2'), None),
    ('aa073304-4212-4b79-9e63-26077acef0c2', 'T6 Mining Excavator Speed Enhancer', 3324, '/enhancers/136', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.2'), None),
    ('4e787210-3f4f-4a9b-9b63-bd132e83ecf4', 'T7 Mining Finder Range Enhancer', 3322, '/enhancers/117', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal(1), None),
    ('c890e47a-a2d0-4d5f-92e6-5ff0a280dcde', 'T7 Mining Finder Skill Modification Enhancer', 4526, '/enhancers/127', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.6'), None),
    ('c9b2c70e-91f1-4263-bd7a-d451443a0d57', 'T7 Mining Excavator Speed Enhancer', 4522, '/enhancers/137', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.2'), None),
    ('91fe09d3-d1ec-4214-8fdb-fd4c47c7a84c', 'T8 Mining Finder Range Enhancer', 3323, '/enhancers/118', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal(1), None),
    ('9d659918-72a8-41fc-abe7-a2c14d8741db', 'T9 Mining Finder Depth Enhancer', 3307, '/enhancers/109', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal('0.8'), None),
    ('90280005-d910-4986-ad37-1742099e96e6', 'T9 Mining Finder Range Enhancer', 4530, '/enhancers/119', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal(1), None),
    ('44e0a3db-08e5-458f-ad5b-6b64f44c024a', 'T8 Mining Finder Skill Modification Enhancer', 4523, '/enhancers/128', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal('0.6'), None),
    ('bada6767-30e3-4541-b160-43f1c7534b1f', 'T9 Mining Finder Skill Modification Enhancer', 4527, '/enhancers/129', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal('0.6'), None),
    ('e4bb3572-bef3-445d-8c53-ec291ee6b739', 'T8 Mining Excavator Speed Enhancer', 4565, '/enhancers/138', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal('0.2'), None),
    ('c65f116d-d2e5-43f4-a5fc-ea59cb5b3e65', 'T9 Mining Excavator Speed Enhancer', 4521, '/enhancers/139', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal('0.2'), None),
    ('63534e3e-c4f2-4347-8131-44cf420f276b', 'T10 Mining Finder Range Enhancer', 4528, '/enhancers/120', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal(1), None),
    ('80289839-c0bf-4d59-a037-fe7968b4a729', 'T10 Mining Finder Skill Modification Enhancer', 4524, '/enhancers/130', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal('0.6'), None),
    ('b88b6a97-d0f3-4901-bfad-4f1024ccfb20', 'T10 Mining Excavator Speed Enhancer', 4564, '/enhancers/140', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal('0.2'), None),
]


def _attributes(name: str) -> tuple[Decimal, Decimal | None, str, str]:
    if "Depth" in name:
        return Decimal("7.43"), None, "FINDER", "DEPTH"
    if "Range" in name:
        return Decimal(1), Decimal("0.1"), "FINDER", "RANGE"
    if "Finder" in name and "Skill" in name:
        return Decimal("0.5"), None, "FINDER", "SKILL"
    return Decimal("0.2"), None, "EXCAVATOR", "SPEED"


def _socket(name: str) -> int:
    """Extract the enhancer socket number from its ``T<number>`` prefix."""

    match = re.match(r"^T(\d+)\b", name)
    if match is None:
        raise ValueError(f"Enhancer name has no socket prefix: {name}")
    return int(match.group(1))


def upgrade() -> None:
    bind = op.get_bind()
    tool_enum = sa.Enum("FINDER", "EXCAVATOR", name="enhancer_tool", create_type=False)
    enhancer_type_enum = sa.Enum(
        "SKILL", "DEPTH", "RANGE", "SPEED", name="enhancer_type", create_type=False
    )
    tool_enum.create(bind, checkfirst=True)
    enhancer_type_enum.create(bind, checkfirst=True)

    op.create_table(
        "enhancer",
        sa.Column("item_id", sa.Uuid(), nullable=False),
        sa.Column("bonus", sa.Numeric(), nullable=False),
        sa.Column("decay_improvement", sa.Numeric(), nullable=True),
        sa.Column("socket", sa.Integer(), nullable=False),
        sa.Column("tool", tool_enum, nullable=False),
        sa.Column("type", enhancer_type_enum, nullable=False),
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
    enhancer_table = sa.table(
        "enhancer",
        sa.column("item_id", sa.Uuid()),
        sa.column("bonus", sa.Numeric()),
        sa.column("decay_improvement", sa.Numeric()),
        sa.column("socket", sa.Integer()),
        sa.column("tool", tool_enum),
        sa.column("type", enhancer_type_enum),
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
                "weight": row[9],
                "is_active": True,
                "nexus_url": row[3],
                "description": row[4],
                "is_rare": row[5],
                "is_untradeable": row[6],
                "created_at": row[7],
                "updated_at": row[8],
            }
            for row in ENHANCERS
        ],
    )
    op.bulk_insert(
        enhancer_table,
        [
            {
                "item_id": UUID(row[0]),
                "bonus": _attributes(row[1])[0],
                "decay_improvement": _attributes(row[1])[1],
                "socket": _socket(row[1]),
                "tool": _attributes(row[1])[2],
                "type": _attributes(row[1])[3],
            }
            for row in ENHANCERS
        ],
    )
    op.bulk_insert(
        economy_table,
        [
            {"item_id": UUID(row[0]), "tt": row[10], "decay": row[11]}
            for row in ENHANCERS
        ],
    )


def downgrade() -> None:
    bind = op.get_bind()
    item_ids = [UUID(row[0]) for row in ENHANCERS]
    economy_table = sa.table("economy", sa.column("item_id", sa.Uuid()))
    enhancer_table = sa.table("enhancer", sa.column("item_id", sa.Uuid()))
    item_table = sa.table("item", sa.column("id", sa.Uuid()))
    bind.execute(economy_table.delete().where(economy_table.c.item_id.in_(item_ids)))
    bind.execute(enhancer_table.delete().where(enhancer_table.c.item_id.in_(item_ids)))
    bind.execute(item_table.delete().where(item_table.c.id.in_(item_ids)))
    op.drop_table("enhancer")
    sa.Enum(name="enhancer_type").drop(bind, checkfirst=True)
    sa.Enum(name="enhancer_tool").drop(bind, checkfirst=True)
