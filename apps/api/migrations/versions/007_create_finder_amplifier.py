"""add finder amplifiers and profession level minimum

Revision ID: 007_create_finder_amplifier
Revises: 006_create_excavator
Create Date: 2026-10-22
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

import sqlalchemy as sa
from alembic import op

revision = "007_create_finder_amplifier"
down_revision = "006_create_excavator"
branch_labels = None
depends_on = None

FINDER_AMPLIFIER_TYPE_ID = UUID("549a7d53-f04a-4da9-baa8-b6fae2f4966f")


def _timestamp(value: str) -> datetime | None:
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


FINDER_AMPLIFIERS = [
    ("7d244a31-49fa-402c-914f-b862a33a3ce3", "Terra Amp 9 (L)", 4869, None, Decimal("80"), 15, None, False, False, _timestamp("2026-10-16T15:27:11.351Z"), None, Decimal("0.8000000000000000444089209850062616169452667236328125"), Decimal("400"), Decimal("16")),
    ("3b30246b-b693-4a8f-80db-f2e698eeb7f1", "D-Class Mining Amp (L)", 7029, None, Decimal("20"), 10, None, False, False, _timestamp("2026-10-16T15:27:11.349Z"), None, Decimal("1"), Decimal("160"), Decimal("4")),
    ("cdce4526-7e47-4e8e-945f-3189606977f6", "eMINE Amplifier 2 (L)", 919, None, Decimal("7.5"), 3, None, False, False, _timestamp("2026-10-16T15:27:11.349Z"), None, Decimal("1"), Decimal("105"), Decimal("1.5")),
    ("06291015-25c6-4a3f-a204-f0d60cf11185", "Level 1 Finder Amplifier", 919, None, Decimal("1.3000000000000000444089209850062616169452667236328125"), 1, None, False, False, _timestamp("2026-10-16T15:27:11.349Z"), None, Decimal("1"), Decimal("78"), Decimal("0.25")),
    ("ac0eed3d-d518-409e-baa3-5611873bf40a", "Level 1 Finder Amplifier (L)", 919, None, Decimal("1.3000000000000000444089209850062616169452667236328125"), 1, None, False, False, _timestamp("2026-10-16T15:27:11.349Z"), None, Decimal("1"), Decimal("78"), Decimal("0.25")),
    ("5b7364b3-a0be-4bbd-9d2d-7fb93bd32c92", "Level 2 Finder Amplifier Light (L)", 919, None, Decimal("2.5"), 1, None, False, False, _timestamp("2026-10-16T15:27:11.349Z"), None, Decimal("0.5"), Decimal("50"), Decimal("0.5")),
    ("b6c5bfc5-f380-4ce8-a68f-e0a3a5ac0f2c", "Level 3 Finder Amplifier", 919, None, Decimal("5"), 2, None, False, False, _timestamp("2026-10-16T15:27:11.349Z"), None, Decimal("1"), Decimal("100"), Decimal("1")),
    ("27f371f8-4bb3-435e-a6dc-51584fcdfae7", "Level 3 Finder Amplifier (L)", 919, None, Decimal("5"), 2, None, False, False, _timestamp("2026-10-16T15:27:11.349Z"), None, Decimal("1"), Decimal("114"), Decimal("1")),
    ("239f41f2-2546-4d09-a579-7bcb314911cf", "Level 3 Finder Amplifier 'Achilles' (L)", 919, None, Decimal("5"), 2, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("1"), Decimal("131"), Decimal("1")),
    ("1aa3df06-9aad-4847-a8b6-d0d4104e9bcb", "Level 4 Finder Amplifier (L)", None, None, Decimal("7.5"), 4, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("1"), Decimal("150"), Decimal("1.5")),
    ("0ad661a4-2f85-4a2f-80ec-e5f0c4841090", "Level 3 Finder Amplifier Light (L)", 919, None, Decimal("5"), 2, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("0.5"), Decimal("75"), Decimal("1")),
    ("ecca1ed5-0547-4f88-8a5d-9afb2c84ce28", "Level 4 Finder Amplifier", 919, None, Decimal("7.5"), 3, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("1"), Decimal("150"), Decimal("1.5")),
    ("ed142630-19ba-4893-9c2a-948e835c316a", "Level 5 Finder Amplifier (L)", 919, None, Decimal("10"), 3, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("1"), Decimal("200"), Decimal("2")),
    ("e44c6f11-d31b-4348-8016-9510416bffdb", "Level 6 Finder Amplifier (L)", 919, None, Decimal("12.5"), 6, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("1"), Decimal("250"), Decimal("2.5")),
    ("4e4b9411-2824-45b1-9985-688873e902c8", "Level 7 Finder Amplifier", 919, None, Decimal("15"), 4, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("1"), Decimal("120"), Decimal("3")),
    ("ebc595a7-397d-4eee-97a6-1b2e58ce9f21", "Level 7 Finder Amplifier (L)", 919, None, Decimal("15"), 4, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("1"), Decimal("120"), Decimal("3")),
    ("b36a0c2f-e16c-4861-9527-6abc3642b522", "Level 7 Finder Amplifier 'Athena' (L)", 919, None, Decimal("16"), 16, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("1"), Decimal("198"), Decimal("3.20000000000000017763568394002504646778106689453125")),
    ("9c55f0a9-3f93-48a0-972f-e3f5e8ebdb52", "Level 8 Finder Amplifier", 919, None, Decimal("20"), 5, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("1"), Decimal("160"), Decimal("4")),
    ("d46b3176-ff3a-4bd5-90f0-3f5019651067", "Level 2 Finder Amplifier", 919, None, Decimal("2.5"), 1, None, False, False, _timestamp("2026-10-16T15:27:11.351Z"), None, Decimal("1"), Decimal("78"), Decimal("0.5")),
    ("8c54286f-550e-4d81-aa67-64e1721b4507", "Level 2 Finder Amplifier (L)", 919, None, Decimal("2.5"), 1, None, False, False, _timestamp("2026-10-16T15:27:11.351Z"), None, Decimal("1"), Decimal("100"), Decimal("0.5")),
    ("cc38a93d-c14d-426f-ae69-5eebee784155", "Level 2 Finder Amplifier, SGA Edition", 919, None, Decimal("2.5"), 1, None, False, False, _timestamp("2026-10-16T15:27:11.351Z"), None, Decimal("0.5"), Decimal("78"), Decimal("0.5")),
    ("2c25b3d1-06b1-4893-94c2-8ea66fdb0c42", "Level 3 Finder Amplifier, SGA Edition", 919, None, Decimal("5"), 2, None, False, False, _timestamp("2026-10-16T15:27:11.351Z"), None, Decimal("0.5"), Decimal("100"), Decimal("1")),
    ("acf6d1e5-41d0-486f-b861-2460c8cce59b", "Mayhem Level 1 Finder Amplifier Mini", None, None, Decimal("1"), 10, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("1"), Decimal("100"), Decimal("0.00200000000000000004163336342344337026588618755340576171875")),
    ("64acff38-5546-41ba-a11d-cb149ed036a5", "Terra Amp 3 Gold Rush", None, None, Decimal("12.5"), 3, None, False, False, _timestamp("2026-10-16T15:27:11.351Z"), None, Decimal("0.8000000000000000444089209850062616169452667236328125"), Decimal("300"), Decimal("2.5")),
    ("b2a3ba46-7d6a-4a2c-b358-369c81fae49b", "Terra Amp 5 Gold Rush", None, None, Decimal("22.5"), 5, None, False, False, _timestamp("2026-10-16T15:27:11.351Z"), None, Decimal("0.8000000000000000444089209850062616169452667236328125"), Decimal("325"), Decimal("4.5")),
    ("9ac4a4fb-19a0-4ddc-9f21-028bc40278e3", "Level 5 Finder Amplifier", 919, None, Decimal("10"), 3, None, False, False, _timestamp("2026-10-16T15:27:11.351Z"), None, Decimal("1"), Decimal("114"), Decimal("2")),
    ("ea94c6ec-89be-473a-83bd-6d383c4cf8fc", "Level 8 Finder Amplifier (L)", 919, None, Decimal("20"), 5, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("1"), Decimal("160"), Decimal("4")),
    ("95697efb-9561-4c8a-b87f-2117b3f1681c", "Level 2 Finder Amplifier 'Achilles' (L)", None, None, Decimal("2.5"), 1, None, False, False, _timestamp("2026-10-16T15:27:11.351Z"), None, Decimal("0.560000000000000053290705182007513940334320068359375"), Decimal("115"), Decimal("0.5")),
    ("1b8efa5f-e11c-4853-a5ea-3b4a70c94278", "Cheeky Finder Amp (L)", 7029, None, Decimal("2.5"), 1, None, False, False, _timestamp("2026-10-16T15:27:11.349Z"), None, Decimal("0.5"), Decimal("50"), Decimal("0.5")),
    ("c5346e65-f203-4abb-807d-e225dadea3cf", "eMINE Amplifier 1 (L)", 919, None, Decimal("3.79999999999999982236431605997495353221893310546875"), 3, None, False, False, _timestamp("2026-10-16T15:27:11.349Z"), None, Decimal("1"), Decimal("105"), Decimal("0.75")),
    ("41d33668-8f52-4538-ac6e-b170c5f27ca8", "Level 1 Finder Amplifier 'Achilles' (L)", 919, None, Decimal("1.3000000000000000444089209850062616169452667236328125"), 1, None, False, False, _timestamp("2026-10-16T15:27:11.349Z"), None, Decimal("1"), Decimal("89"), Decimal("0.25")),
    ("2e2e514d-5e17-4c4a-ad0b-0c45d2f3dd97", "Level 1 Finder Amplifier Light (L)", 919, None, Decimal("1.1999999999999999555910790149937383830547332763671875"), 1, None, False, False, _timestamp("2026-10-16T15:27:11.351Z"), None, Decimal("1"), Decimal("30"), Decimal("0.25")),
    ("b71a1ff7-f8f2-4756-b318-41d4cd252a98", "Level VIII Finder Amplifier 'Athena' (L)", 919, None, Decimal("19"), 18, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("1"), Decimal("208"), Decimal("3.79999999999999982236431605997495353221893310546875")),
    ("470e69de-c8ac-4e45-9a64-e61d475ee58a", "Terra Amp 1 (L)", 4869, None, Decimal("4"), 1, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("0.8000000000000000444089209850062616169452667236328125"), Decimal("45"), Decimal("0.8000000000000000444089209850062616169452667236328125")),
    ("5861cbb0-f8fd-4ed0-af12-536198586652", "Terra Amp 1 Gold Rush", 4869, None, Decimal("4"), 1, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("0.8000000000000000444089209850062616169452667236328125"), Decimal("45"), Decimal("0.8000000000000000444089209850062616169452667236328125")),
    ("7604e6cf-a803-4080-af90-5f19ba66817d", "Terra Amp 2 (L)", 4869, None, Decimal("8"), 2, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("0.8000000000000000444089209850062616169452667236328125"), Decimal("195"), Decimal("1.600000000000000088817841970012523233890533447265625")),
    ("8ff53018-f4a0-418f-bdc4-b5fd88d67e60", "Terra Amp 8 (L)", 4869, None, Decimal("60"), 12, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("0.8000000000000000444089209850062616169452667236328125"), Decimal("385"), Decimal("12")),
    ("393c02f8-ad53-4747-afb5-a4525c20efbe", "Terra Amp 3 (L)", 4869, None, Decimal("12.5"), 3, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("0.8000000000000000444089209850062616169452667236328125"), Decimal("300"), Decimal("2.5")),
    ("0439598d-d393-4b3d-b645-f63301450ca3", "Level V Finder Amplifier 'Athena' (L)", None, None, Decimal("11"), 12, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("1"), Decimal("178"), Decimal("2.20000000000000017763568394002504646778106689453125")),
    ("13ce9a6a-58a4-487f-a959-ea1f03dce1d0", "Sabad Finder Amp V1 (L)", None, None, Decimal("5.5"), None, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("0.8000000000000000444089209850062616169452667236328125"), Decimal("165"), Decimal("1.100000000000000088817841970012523233890533447265625")),
    ("3749386f-24af-480c-aecd-cbdf66888a53", "Terra Amp 4 (L)", 4869, None, Decimal("17.5"), 4, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("0.8000000000000000444089209850062616169452667236328125"), Decimal("315"), Decimal("3.5")),
    ("c7455899-0c59-4d81-bc6c-9963eeb5aae8", "Terra Amp 5 (L)", 4869, None, Decimal("22.5"), 5, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("0.8000000000000000444089209850062616169452667236328125"), Decimal("325"), Decimal("4.5")),
    ("73e5dc88-1a06-4b98-a69f-aa1cc3c75c84", "Terra Amp 6 (L)", 4869, None, Decimal("30"), 7, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("0.8000000000000000444089209850062616169452667236328125"), Decimal("338"), Decimal("6")),
    ("915cb428-aa42-492c-a072-5bf401c293bd", "Terra Amp 7 (L)", 4869, None, Decimal("45"), 9, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("0.8000000000000000444089209850062616169452667236328125"), Decimal("360"), Decimal("9")),
    ("c759b629-0222-4703-9489-e27bdf3880f8", "Terra Amp 10 (L)", 4869, None, Decimal("100"), 18, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("0.8000000000000000444089209850062616169452667236328125"), Decimal("442"), Decimal("20")),
    ("b6e40392-5c58-4c8b-bebe-b877917d356d", "Terra Amp I 'Athena' (L)", 4869, None, Decimal("2"), 4, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("0.8000000000000000444089209850062616169452667236328125"), Decimal("64"), Decimal("0.40000000000000002220446049250313080847263336181640625")),
    ("56fb7be1-d260-4af5-bbc2-326b8d296657", "Terra Amp IV 'Athena' (L)", 4869, None, Decimal("6"), 10, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("0.8000000000000000444089209850062616169452667236328125"), Decimal("134"), Decimal("1.1999999999999999555910790149937383830547332763671875")),
    ("2256e355-02a0-4c09-a91d-38b84462fa0d", "Terra Amp VI 'Athena' (L)", 4869, None, Decimal("13"), 14, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("0.8000000000000000444089209850062616169452667236328125"), Decimal("188"), Decimal("2.600000000000000088817841970012523233890533447265625")),
    ("19e3fe3e-283e-483a-bfca-959275355369", "DSEC Seeker Amplifier II (L)", None, None, Decimal("6.70000000000000017763568394002504646778106689453125"), 3, None, False, False, _timestamp("2026-10-16T15:27:11.349Z"), None, Decimal("1.1999999999999999555910790149937383830547332763671875"), Decimal("125"), Decimal("1.3300000000000000710542735760100185871124267578125")),
    ("5900d148-e053-4c64-8909-f37ba4f18b86", "DSEC Seeker Amplifier III (L)", None, None, Decimal("14.300000000000000710542735760100185871124267578125"), 7, None, False, False, _timestamp("2026-10-16T15:27:11.349Z"), None, Decimal("1.399999999999999911182158029987476766109466552734375"), Decimal("268"), Decimal("2.850000000000000088817841970012523233890533447265625")),
    ("a682b2d1-b7e0-4089-b661-d0a00c1fb505", "Level 9 Finder Amplifier (L)", 919, None, Decimal("25"), 6, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("1"), Decimal("260"), Decimal("5")),
    ("929e3e4c-2967-413d-8d0c-921b92ea3005", "Level 10 Finder Amplifier (L)", 919, None, Decimal("37.5"), 8, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("1"), Decimal("300"), Decimal("7.5")),
    ("40e354a7-4df0-4705-95ad-cee54b86998b", "Level 11 Finder Amplifier (L)", 919, None, Decimal("50"), 10, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("1"), Decimal("350"), Decimal("10")),
    ("36ddfcf3-179b-401a-901a-80596b6195dc", "Level 12 Finder Amplifier (L)", 919, None, Decimal("75"), 15, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("1"), Decimal("255"), Decimal("15")),
    ("16c38143-c3c3-44a5-9e8f-9134f0397f86", "Level 13 Finder Amplifier (L)", 919, None, Decimal("100"), 20, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("1"), Decimal("340"), Decimal("20")),
    ("266f81ed-5b12-4697-8a70-28c025c9d446", "Level II Finder Amplifier 'Athena' (L)", 7028, None, Decimal("3"), 6, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("1"), Decimal("82"), Decimal("0.59999999999999997779553950749686919152736663818359375")),
    ("1f196fa3-9259-4da4-a34f-70878fd0c086", "Level III Finder Amplifier 'Athena' (L)", 7029, None, Decimal("4"), 8, None, False, False, _timestamp("2026-10-16T15:27:11.350Z"), None, Decimal("1"), Decimal("102"), Decimal("0.8000000000000000444089209850062616169452667236328125")),
]


def upgrade() -> None:
    op.add_column(
        "item_detail",
        sa.Column("profession_level_min", sa.Numeric(), nullable=True, server_default=None),
    )

    item_table = sa.table(
        "item",
        sa.column("id", sa.Uuid()),
        sa.column("name", sa.String()),
        sa.column("img_id", sa.Integer()),
        sa.column("weight", sa.Numeric()),
        sa.column("nexus_url", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("is_rare", sa.Boolean()),
        sa.column("is_untradeable", sa.Boolean()),
        sa.column("type_id", sa.Uuid()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    item_detail_table = sa.table(
        "item_detail",
        sa.column("item_id", sa.Uuid()),
        sa.column("efficiency", sa.Numeric()),
        sa.column("profession_level_min", sa.Numeric()),
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
                "nexus_url": row[3],
                "description": row[6],
                "is_rare": row[7],
                "is_untradeable": row[8],
                "type_id": FINDER_AMPLIFIER_TYPE_ID,
                "created_at": row[9],
                "updated_at": row[10],
            }
            for row in FINDER_AMPLIFIERS
        ],
    )
    op.bulk_insert(
        item_detail_table,
        [
            {
                "item_id": UUID(row[0]),
                "efficiency": row[4],
                "profession_level_min": row[5],
            }
            for row in FINDER_AMPLIFIERS
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
            for row in FINDER_AMPLIFIERS
        ],
    )


def downgrade() -> None:
    bind = op.get_bind()
    item_ids = [UUID(row[0]) for row in FINDER_AMPLIFIERS]

    economy_table = sa.table("economy", sa.column("item_id", sa.Uuid()))
    item_detail_table = sa.table("item_detail", sa.column("item_id", sa.Uuid()))
    item_table = sa.table("item", sa.column("id", sa.Uuid()))
    bind.execute(economy_table.delete().where(economy_table.c.item_id.in_(item_ids)))
    bind.execute(item_detail_table.delete().where(item_detail_table.c.item_id.in_(item_ids)))
    bind.execute(item_table.delete().where(item_table.c.id.in_(item_ids)))
    op.drop_column("item_detail", "profession_level_min")
