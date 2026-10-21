"""create type table and initial types

Revision ID: 001_create_type
Revises: 000_create_category
Create Date: 2026-10-21
"""

from datetime import UTC, datetime
from uuid import UUID

import sqlalchemy as sa
from alembic import op

revision = "001_create_type"
down_revision = "000_create_category"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "type",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column("is_stackable", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["category.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    type_table = sa.table(
        "type",
        sa.column("id", sa.Uuid()),
        sa.column("category_id", sa.Uuid()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        sa.column("is_active", sa.Boolean()),
        sa.column("is_stackable", sa.Boolean()),
        sa.column("name", sa.String()),
    )

    op.bulk_insert(
        type_table,
        [
            {
                "id": UUID("3cf59ae8-0a13-4dac-9b9e-e0f6824a082f"),
                "category_id": UUID("761d24c4-8bc5-42e2-b30d-b749bc4d3eb4"),
                "created_at": datetime(
                    2026, 10, 4, 13, 46, 6, 360651, tzinfo=UTC
                ),
                "updated_at": datetime(
                    2026, 10, 9, 14, 57, 59, 871000, tzinfo=UTC
                ),
                "is_active": True,
                "is_stackable": False,
                "name": "Finder",
            },
            {
                "id": UUID("a81ff2c2-6d26-49bd-9dd7-73c38c64773d"),
                "category_id": UUID("761d24c4-8bc5-42e2-b30d-b749bc4d3eb4"),
                "created_at": datetime(
                    2026, 10, 11, 23, 22, 3, 747000, tzinfo=UTC
                ),
                "updated_at": None,
                "is_active": True,
                "is_stackable": False,
                "name": "Excavator",
            },
            {
                "id": UUID("4f1a325f-ff6a-4c79-812c-1dda709a4f4d"),
                "category_id": UUID("761d24c4-8bc5-42e2-b30d-b749bc4d3eb4"),
                "created_at": datetime(
                    2026, 10, 11, 23, 31, 39, 29000, tzinfo=UTC
                ),
                "updated_at": None,
                "is_active": True,
                "is_stackable": False,
                "name": "Refiner",
            },
            {
                "id": UUID("155f05ef-29b7-478a-aaa7-7d8db93e8811"),
                "category_id": UUID("4cafc352-08b6-4342-9c84-715a1649e62a"),
                "created_at": datetime(
                    2026, 10, 11, 23, 44, 31, 710000, tzinfo=UTC
                ),
                "updated_at": None,
                "is_active": True,
                "is_stackable": True,
                "name": "Enhancer",
            },
            {
                "id": UUID("549a7d53-f04a-4da9-baa8-b6fae2f4966f"),
                "category_id": UUID("4cafc352-08b6-4342-9c84-715a1649e62a"),
                "created_at": datetime(
                    2026, 10, 14, 14, 49, 23, 397000, tzinfo=UTC
                ),
                "updated_at": None,
                "is_active": True,
                "is_stackable": False,
                "name": "Finder Amplifier",
            },
            {
                "id": UUID("2FE7B2D0-73CB-4E53-96A6-3BC32C5E7188"),
                "category_id": UUID("88B86318-0F7B-4D68-B095-D0DC313324A5"),
                "created_at": datetime(2025, 11, 23, 11, 59, 1, 595717),
                "updated_at": datetime(
                    2026, 10, 13, 10, 12, 59, 637000, tzinfo=UTC
                ),
                "is_active": True,
                "is_stackable": True,
                "name": "Animal Oil",
            },
            {
                "id": UUID("3D9AE042-489C-4996-88D3-0EACABFABE92"),
                "category_id": UUID("88B86318-0F7B-4D68-B095-D0DC313324A5"),
                "created_at": datetime(2025, 11, 23, 11, 59, 1, 595717),
                "updated_at": datetime(
                    2026, 10, 13, 10, 13, 20, 36000, tzinfo=UTC
                ),
                "is_active": True,
                "is_stackable": True,
                "name": "Natural Material",
            },
            {
                "id": UUID("5DFA9973-5F3F-4FF5-A98B-BB585E1E39D5"),
                "category_id": UUID("88B86318-0F7B-4D68-B095-D0DC313324A5"),
                "created_at": datetime(2025, 11, 23, 11, 59, 1, 595717),
                "updated_at": None,
                "is_active": True,
                "is_stackable": True,
                "name": "Refined Enmatter",
            },
            {
                "id": UUID("B274D976-0D05-4415-98C6-08798B14A6A2"),
                "category_id": UUID("88B86318-0F7B-4D68-B095-D0DC313324A5"),
                "created_at": datetime(2025, 11, 23, 11, 59, 1, 595717),
                "updated_at": None,
                "is_active": True,
                "is_stackable": True,
                "name": "Refined Ore",
            },
            {
                "id": UUID("F39D2654-E076-4971-902F-B28511E12E48"),
                "category_id": UUID("88B86318-0F7B-4D68-B095-D0DC313324A5"),
                "created_at": datetime(2025, 11, 23, 11, 59, 1, 595717),
                "updated_at": None,
                "is_active": True,
                "is_stackable": True,
                "name": "Consumable",
            },
            {
                "id": UUID("25F61687-F547-4712-8B91-786889BA6CF1"),
                "category_id": UUID("88B86318-0F7B-4D68-B095-D0DC313324A5"),
                "created_at": datetime(2025, 11, 23, 11, 59, 1, 595717),
                "updated_at": None,
                "is_active": True,
                "is_stackable": True,
                "name": "Ore",
            },
            {
                "id": UUID("2E4D69AA-BBEC-44E7-B4A3-4F3EC17B6C78"),
                "category_id": UUID("88B86318-0F7B-4D68-B095-D0DC313324A5"),
                "created_at": datetime(2025, 11, 23, 11, 59, 1, 595717),
                "updated_at": datetime(
                    2026, 10, 13, 10, 13, 29, 228000, tzinfo=UTC
                ),
                "is_active": True,
                "is_stackable": True,
                "name": "Enmatter",
            },
            {
                "id": UUID("0134200c-be50-4b79-9214-ae1994bbe857"),
                "category_id": UUID("88B86318-0F7B-4D68-B095-D0DC313324A5"),
                "created_at": datetime(
                    2026, 10, 14, 22, 7, 19, 123082, tzinfo=UTC
                ),
                "updated_at": None,
                "is_active": True,
                "is_stackable": True,
                "name": "Fragment",
            },
            {
                "id": UUID("a691ee98-69e8-45be-ab45-c481387ee668"),
                "category_id": UUID("88B86318-0F7B-4D68-B095-D0DC313324A5"),
                "created_at": datetime(
                    2026, 10, 18, 12, 2, 5, 997534, tzinfo=UTC
                ),
                "updated_at": None,
                "is_active": True,
                "is_stackable": False,
                "name": "Food",
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("type")
