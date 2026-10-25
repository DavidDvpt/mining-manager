"""Persistence operations for user profiles."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import Profile


class ProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, *, user_id: UUID, email: str, firstname: str | None,
                     lastname: str | None, avatar_name: str | None = None) -> Profile:
        profile = Profile(
            user_id=user_id, email=email, firstname=firstname,
            lastname=lastname, avatar_name=avatar_name,
        )
        self._session.add(profile)
        await self._session.flush()
        return profile

    async def get_by_user_id(self, user_id: UUID) -> Profile | None:
        return await self._session.scalar(
            select(Profile).where(Profile.user_id == user_id)
        )
