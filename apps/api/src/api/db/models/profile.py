"""Personal information associated with a login user."""

from uuid import UUID
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .user import User


class Profile(Base):
    __tablename__ = "profile"

    user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    firstname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lastname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    avatar_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)

    user: Mapped["User"] = relationship(back_populates="profile")

