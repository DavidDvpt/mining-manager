"""Authentication use cases."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AppError
from api.db.models import User
from api.db.repositories import UserRepository
from api.services.password_service import hash_password, verify_password


def serialize_user(user: User) -> dict:
    return {
        "id": str(user.id),
        "role": user.role.value,
        "pseudo": user.pseudo,
    }


async def signup(session: AsyncSession, *, pseudo: str, password: str) -> None:
    user_repo = UserRepository(session)
    if await user_repo.get_by_pseudo(pseudo):
        raise AppError(409, "Pseudo already in use")
    await user_repo.create(pseudo=pseudo, password_hash=hash_password(password))
    await session.commit()


async def signin(session: AsyncSession, *, pseudo: str, password: str) -> User:
    user = await UserRepository(session).get_by_pseudo(pseudo)
    if user is None or not user.is_active or not verify_password(user.password_hash, password):
        raise AppError(401, "Identifiants invalides")
    return user


async def me(session: AsyncSession, user_id: UUID) -> dict | None:
    user = await UserRepository(session).get_by_id(user_id)
    return serialize_user(user) if user else None
