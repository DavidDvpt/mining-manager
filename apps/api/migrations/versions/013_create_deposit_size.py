"""create and seed deposit size thresholds"""

from decimal import Decimal

import sqlalchemy as sa
from alembic import op

revision = "013_create_deposit_size"
down_revision = "012_create_profile"
branch_labels = None
depends_on = None


DEPOSIT_SIZES = [
    (1, "I", "Minimal", "0.05", "0.24"),
    (1, "II", "Tiny", "0.25", "0.99"),
    (1, "III", "Very Poor", "1", "1.99"),
    (1, "IV", "Poor", "2", "2.99"),
    (1, "V", "Small", "3", "4.49"),
    (1, "VI", "Modest", "4.5", "5.99"),
    (1, "VII", "Average", "6", "7.99"),
    (1, "VIII", "Medium", "8", "11.99"),
    (2, "IX", "Ample", "12", "17.99"),
    (3, "X", "Considerable", "18", "24.99"),
    (6, "XI", "Sizable", "25", "34.99"),
    (10, "XII", "Large", "35", "49.99"),
    (18, "XIII", "Abundant", "50", "74.99"),
    (24, "XIV", "Great", "75", "124.99"),
    (24, "XV", "Substantial", "125", "199.99"),
    (24, "XVI", "Significant", "200", "299.99"),
    (24, "XVII", "Plentiful", "300", "449.99"),
    (24, "XVIII", "Huge", "450", "649.99"),
    (24, "XIX", "Extremely Large", "650", "799.99"),
    (24, "XX", "Massive", "800", "1199.99"),
    (24, "XXI", "Vast", "1200", "2499.99"),
    (24, "XXII", "Enormous", "2500", "4999.99"),
    (24, "XXIII", "Rich", "5000", "24999.99"),
    (24, "XXIV", "Gigantic", "25000", "99999.99"),
    (24, "XXV", "Mammoth", "100000", "249999.99"),
    (24, "XXVI", "Colossal", "250000", "499999.99"),
    (24, "XXVII", "Immense", "500000", "999999999.99"),
]


def upgrade() -> None:
    op.create_table(
        "deposit_size",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("roman_size", sa.String(length=10), nullable=False),
        sa.Column("size_label", sa.String(length=50), nullable=False),
        sa.Column("min", sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column("max", sa.Numeric(precision=20, scale=2), nullable=False),
        sa.CheckConstraint("min >= 0", name="ck_deposit_size_min_non_negative"),
        sa.CheckConstraint("max >= min", name="ck_deposit_size_max_gte_min"),
        sa.PrimaryKeyConstraint("id"),
    )

    table = sa.table(
        "deposit_size",
        sa.column("size", sa.Integer()),
        sa.column("roman_size", sa.String(length=10)),
        sa.column("size_label", sa.String(length=50)),
        sa.column("min", sa.Numeric(precision=20, scale=2)),
        sa.column("max", sa.Numeric(precision=20, scale=2)),
    )
    op.bulk_insert(
        table,
        [
            {
                "size": row[0],
                "roman_size": row[1],
                "size_label": row[2],
                "min": Decimal(row[3]),
                "max": Decimal(row[4]),
            }
            for row in DEPOSIT_SIZES
        ],
    )


def downgrade() -> None:
    op.drop_table("deposit_size")
