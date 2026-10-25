"""Authentication dependencies for cookie users and internal callers."""

from secrets import compare_digest
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request

from api.core.config import get_settings
from api.core.exceptions import AppError
from api.services.jwt_service import decode_token

ACCESS_TOKEN_COOKIE = "access_token"


def _bearer(request: Request) -> str | None:
    scheme, _, token = request.headers.get("Authorization", "").partition(" ")
    return token if scheme.lower() == "bearer" and token else None


def _decode(token: str) -> dict:
    try:
        return decode_token(secret=get_settings().jwt_access_secret, token=token)
    except Exception:
        raise AppError(401, "Unauthorized") from None


def get_current_user(request: Request) -> dict:
    token = request.cookies.get(ACCESS_TOKEN_COOKIE)
    if not token:
        raise AppError(401, "Unauthorized")
    payload = _decode(token)
    try:
        return {**payload, "id": UUID(str(payload["sub"]))}
    except (KeyError, ValueError):
        raise AppError(401, "Unauthorized") from None


CurrentUser = Annotated[dict, Depends(get_current_user)]


def get_internal_user(request: Request) -> dict:
    token = _bearer(request)
    configured = get_settings().internal_api_token
    if not token or not configured or not compare_digest(token, configured):
        raise AppError(401, "Unauthorized")
    return {"id": "internal", "role": "ADMIN", "pseudo": "internal"}


InternalUser = Annotated[dict, Depends(get_internal_user)]
