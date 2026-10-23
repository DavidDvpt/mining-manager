"""create enhancer table and seed enhancers

Revision ID: 006_create_enhancer
Revises: 005_create_finder_amplifier
Create Date: 2026-10-23
"""

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
    ('bc57050c-5f46-4a80-af62-be46c8347c3a', 'T1 Mining Finder Depth Enhancer', 3286, '/enhancers/101', None, False, False, _timestamp('2026-10-11T23:44:31.983Z'), None, Decimal('0.01'), Decimal('0.8'), None),
    ('91d56845-a247-4c23-8e94-c1aedc666809', 'T3 Mining Finder Depth Enhancer', 3317, '/enhancers/103', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.8'), None),
    ('58f78cdf-6040-44c7-9479-b4a5eb562320', 'T4 Mining Finder Depth Enhancer', 3306, '/enhancers/104', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.8'), None),
    ('5ef89dc4-88db-4bdb-a0b6-96507d15cc63', 'T5 Mining Finder Depth Enhancer', 3341, '/enhancers/105', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.8'), None),
    ('59e9055e-9215-4156-86b5-7c29457f1d77', 'T7 Mining Finder Depth Enhancer', 4112, '/enhancers/107', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.8'), None),
    ('0895c620-51b8-4588-9316-d54214cfc5e3', 'T8 Mining Finder Depth Enhancer', 4114, '/enhancers/108', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal('0.8'), None),
    ('a135c1e8-56ab-4b3e-bf46-2205b0d6495c', 'T10 Mining Finder Depth Enhancer', 4529, '/enhancers/110', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal('0.8'), None),
    ('1d34f2ac-6023-446e-aa39-9057a8daa646', 'T2 Mining Finder Range Enhancer', 3318, '/enhancers/112', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal(1), None),
    ('ffba5b8b-b5f0-49a7-ba35-717869dd9cab', 'T2 Mining Finder Depth Enhancer', 3305, '/enhancers/102', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.8'), None),
    ('c5438f00-6306-4ef0-9450-ea643e17a5ea', 'T1 Mining Finder Range Enhancer', 3283, '/enhancers/111', None, False, False, _timestamp('2026-10-11T23:44:31.983Z'), None, Decimal('0.01'), Decimal(1), None),
    ('a40d9945-ec55-4e47-a0ba-82b69d45c4cb', 'T1 Mining Finder Skill Modification Enhancer', 3256, '/enhancers/121', None, False, False, _timestamp('2026-10-11T23:44:31.983Z'), None, Decimal('0.01'), Decimal('0.6'), None),
    ('d1c2150e-a8da-4de3-841d-df70282156cf', 'T2 Mining Finder Skill Modification Enhancer', 3340, '/enhancers/122', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.6'), None),
    ('b7a282b7-02a9-4950-abf9-bb61df2a7fba', 'T1 Mining Excavator Speed Enhancer', 3255, '/enhancers/131', None, False, False, _timestamp('2026-10-11T23:44:31.983Z'), None, Decimal('0.01'), Decimal('0.2'), None),
    ('58b83aba-fb9c-4e62-b8e6-5505f7191eef', 'T2 Mining Excavator Speed Enhancer', 3280, '/enhancers/132', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.2'), None),
    ('64a2e564-559c-433f-84be-c476d9bcf123', 'T3 Mining Finder Range Enhancer', 3319, '/enhancers/113', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal(1), None),
    ('2b76bcd4-eb53-4f3d-af6f-222cc68edb60', 'T3 Mining Finder Skill Modification Enhancer', 3269, '/enhancers/123', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.6'), None),
    ('9b7cc4e1-a8ef-4d82-ad6b-f0ef8218eeea', 'T3 Mining Excavator Speed Enhancer', 3281, '/enhancers/133', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.2'), None),
    ('d445caa2-93e8-46a7-96a6-0fc3b1065e07', 'T4 Mining Finder Range Enhancer', 3320, '/enhancers/114', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal(1), None),
    ('0a3cf086-7e70-42d4-a357-a321c05b9cbe', 'T4 Mining Finder Skill Modification Enhancer', 4375, '/enhancers/124', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.6'), None),
    ('547beae0-81a7-4f59-8ddb-a2187abcc684', 'T4 Mining Excavator Speed Enhancer', 3282, '/enhancers/134', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.2'), None),
    ('c993d652-d4b2-40a0-80b2-24821375ac3e', 'T6 Mining Finder Depth Enhancer', 4113, '/enhancers/106', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.8'), None),
    ('380f6015-6f92-41d5-b7ce-a173727b7e5d', 'T5 Mining Finder Range Enhancer', 3321, '/enhancers/115', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal(1), None),
    ('8d29d46c-cfe7-4b46-b21f-2343c11a4dfb', 'T6 Mining Finder Range Enhancer', 3339, '/enhancers/116', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal(1), None),
    ('a2bab5a4-036c-42c8-9fe3-6c19c9422b89', 'T5 Mining Finder Skill Modification Enhancer', 3308, '/enhancers/125', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.6'), None),
    ('65906217-8982-4838-adc6-3f7e8a6b5c3a', 'T6 Mining Finder Skill Modification Enhancer', 4525, '/enhancers/126', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.6'), None),
    ('e47e236d-f1d5-4b6d-bc8b-c4048b4410fc', 'T5 Mining Excavator Speed Enhancer', 3338, '/enhancers/135', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.2'), None),
    ('e685b485-37e1-4ff6-9599-cdaf3d703dbd', 'T6 Mining Excavator Speed Enhancer', 3324, '/enhancers/136', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.2'), None),
    ('bcdbbdc8-c89e-4e6b-b1ed-230fbd9ef3b2', 'T7 Mining Finder Range Enhancer', 3322, '/enhancers/117', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal(1), None),
    ('0010c7ab-964a-44d2-8141-4c57b07e075a', 'T7 Mining Finder Skill Modification Enhancer', 4526, '/enhancers/127', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.6'), None),
    ('cda6a90e-27bf-453d-a53b-873f588075c3', 'T7 Mining Excavator Speed Enhancer', 4522, '/enhancers/137', None, False, False, _timestamp('2026-10-11T23:44:31.984Z'), None, Decimal('0.01'), Decimal('0.2'), None),
    ('a8af0f63-bc43-49ef-a36b-095b4a12d8cd', 'T8 Mining Finder Range Enhancer', 3323, '/enhancers/118', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal(1), None),
    ('e1244a1d-5a8d-4c4f-b3d0-ad3f8a448cbd', 'T9 Mining Finder Depth Enhancer', 3307, '/enhancers/109', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal('0.8'), None),
    ('b8f4d25f-afc3-4a96-8ae7-c8a2f103a592', 'T9 Mining Finder Range Enhancer', 4530, '/enhancers/119', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal(1), None),
    ('bb049ecd-2cf3-4e3b-bc8d-43feea445b9e', 'T8 Mining Finder Skill Modification Enhancer', 4523, '/enhancers/128', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal('0.6'), None),
    ('2197cae9-f3f9-4c69-a007-3061037182a7', 'T9 Mining Finder Skill Modification Enhancer', 4527, '/enhancers/129', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal('0.6'), None),
    ('2a627b6f-a22c-43e0-8d30-050dec9bcae5', 'T8 Mining Excavator Speed Enhancer', 4565, '/enhancers/138', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal('0.2'), None),
    ('39dc163e-98d8-4328-842b-c30e42a0b5ac', 'T9 Mining Excavator Speed Enhancer', 4521, '/enhancers/139', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal('0.2'), None),
    ('45421beb-aff1-4d2d-a03d-4cff019c0634', 'T10 Mining Finder Range Enhancer', 4528, '/enhancers/120', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal(1), None),
    ('ad64c99a-9aa7-48a1-998b-2102ee2a0595', 'T10 Mining Finder Skill Modification Enhancer', 4524, '/enhancers/130', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal('0.6'), None),
    ('96de7d9f-7a74-454e-9aa2-7c1bc6bb3fc1', 'T10 Mining Excavator Speed Enhancer', 4564, '/enhancers/140', None, False, False, _timestamp('2026-10-11T23:44:31.985Z'), None, Decimal('0.01'), Decimal('0.2'), None),
]


def _attributes(name: str) -> tuple[Decimal, Decimal | None, str, str]:
    if "Depth" in name:
        return Decimal("7.43"), None, "FINDER", "DEPTH"
    if "Range" in name:
        return Decimal(1), Decimal("0.1"), "FINDER", "RANGE"
    if "Finder" in name and "Skill" in name:
        return Decimal("0.5"), None, "FINDER", "SKILL"
    return Decimal("0.2"), None, "EXCAVATOR", "SPEED"


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
