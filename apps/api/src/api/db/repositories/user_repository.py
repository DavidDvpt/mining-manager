"""Persistence operations for users."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import Role, User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self._session.scalar(select(User).where(User.id == user_id))

    async def get_by_pseudo(self, pseudo: str) -> User | None:
        return await self._session.scalar(select(User).where(User.pseudo == pseudo))

    async def create(self, *, pseudo: str, password_hash: str) -> User:
        user = User(
            pseudo=pseudo, password_hash=password_hash, role=Role.USER,
        )
        self._session.add(user)
        await self._session.flush()
        return user
