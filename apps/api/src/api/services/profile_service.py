"""Profile use cases."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import Profile
from api.db.repositories import ProfileRepository


def serialize_profile(profile: Profile) -> dict:
    return {
        "user_id": str(profile.user_id),
        "email": profile.email,
        "firstname": profile.firstname,
        "lastname": profile.lastname,
        "avatar_name": profile.avatar_name,
    }


async def get_profile(session: AsyncSession, user_id: UUID) -> dict | None:
    profile = await ProfileRepository(session).get_by_user_id(user_id)
    return serialize_profile(profile) if profile else None
