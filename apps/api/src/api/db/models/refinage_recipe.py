from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .material import Material
    from .session_refinage import SessionRefinage


class RefinageRecipe(Base):
    """Define the material transformation and the quantity it produces."""

    __tablename__ = "refinage_recipe"
    __table_args__ = (
        CheckConstraint(
            "quantity >= 0", name="ck_refinage_recipe_quantity_non_negative"
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        server_default=text("gen_random_uuid()"),
        primary_key=True,
        nullable=False,
    )
    result: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("material.item_id"),
        nullable=False,
    )
    origin: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("material.item_id"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(nullable=False)

    result_material: Mapped["Material"] = relationship(
        foreign_keys=[result],
        back_populates="result_recipes",
    )
    origin_material: Mapped["Material"] = relationship(
        foreign_keys=[origin],
        back_populates="origin_recipes",
    )
    sessions: Mapped[list["SessionRefinage"]] = relationship(
        back_populates="recipe",
    )
