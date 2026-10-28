"""Authentication use cases."""

import time
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import get_settings
from api.core.exceptions import AppError
from api.db.models import User
from api.db.repositories import UserRepository
from api.services.jwt_service import decode_token, max_age, sign_token
from api.services.password_service import hash_password, verify_password

@dataclass(frozen=True)
class AuthTokens:
    """Tokens and their cookie lifetimes returned by authentication use cases."""

    access_token: str
    access_max_age: int
    refresh_token: str | None
    refresh_max_age: int | None


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


def issue_tokens(
    user: User | dict,
    *,
    access_expires_in: str,
    access_issued_from: str,
) -> AuthTokens:
    """Issue signed access and refresh tokens for an authenticated user."""

    settings = get_settings()
    user_id = user["id"] if isinstance(user, dict) else user.id
    role = user["role"] if isinstance(user, dict) else user.role.value
    pseudo = user["pseudo"] if isinstance(user, dict) else user.pseudo
    access_token = sign_token(
        secret=settings.jwt_access_secret,
        claims={
            "sub": str(user_id),
            "role": role,
            "pseudo": pseudo,
            "token_type": "access",
            "issued_from": access_issued_from,
        },
        expires_in=access_expires_in,
    )

    refresh_token = None
    refresh_max_age = None
    if settings.jwt_refresh_secret:
        refresh_token = sign_token(
            secret=settings.jwt_refresh_secret,
            claims={"sub": str(user_id), "token_type": "refresh"},
            expires_in=settings.jwt_refresh_expires_in,
        )
        refresh_max_age = max_age(settings.jwt_refresh_expires_in)

    return AuthTokens(
        access_token=access_token,
        access_max_age=max_age(access_expires_in),
        refresh_token=refresh_token,
        refresh_max_age=refresh_max_age,
    )


async def refresh_authentication(
    session: AsyncSession, refresh_token: str | None
) -> AuthTokens:
    """Validate an idle-limited refresh token and issue rotated authentication tokens."""

    settings = get_settings()
    if not refresh_token or not settings.jwt_refresh_secret:
        raise AppError(401, "Unauthorized")

    try:
        payload = decode_token(secret=settings.jwt_refresh_secret, token=refresh_token)
        if payload.get("token_type") != "refresh":
            raise ValueError("Not a refresh token")
        user_id = UUID(str(payload["sub"]))
        issued_at = int(payload["iat"])
    except Exception:
        raise AppError(401, "Unauthorized") from None

    if int(time.time()) - issued_at > max_age(settings.jwt_refresh_access_expires_in):
        raise AppError(401, "Session expired")

    user = await UserRepository(session).get_by_id(user_id)
    if user is None or not user.is_active:
        raise AppError(401, "Unauthorized")

    return issue_tokens(
        user,
        access_expires_in=settings.jwt_refresh_access_expires_in,
        access_issued_from="refresh",
    )


async def me(session: AsyncSession, user_id: UUID) -> dict | None:
    user = await UserRepository(session).get_by_id(user_id)
    return serialize_user(user) if user else None


