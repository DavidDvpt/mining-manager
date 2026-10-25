"""Public sign-in/sign-up and cookie-authenticated identity endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import ACCESS_TOKEN_COOKIE, CurrentUser
from api.core.config import get_settings
from api.core.exceptions import AppError
from api.db import get_session
from api.schemas.auth_schema import SignInRequest, SignUpRequest, UserResponse
from api.services import auth_service
from api.services.jwt_service import max_age, sign_token

router = APIRouter(tags=["auth"])
DbSession = Annotated[AsyncSession, Depends(get_session)]


def _set_auth_cookies(response: Response, user) -> None:
    settings = get_settings()
    access_token = sign_token(
        secret=settings.jwt_access_secret,
        claims={"sub": str(user.id), "role": user.role.value, "pseudo": user.pseudo},
        expires_in=settings.jwt_access_expires_in,
    )
    response.set_cookie(
        ACCESS_TOKEN_COOKIE, access_token,
        max_age=max_age(settings.jwt_access_expires_in), httponly=True,
        secure=settings.app_env == "production", samesite="lax", path="/",
    )
    if settings.jwt_refresh_secret:
        refresh_token = sign_token(
            secret=settings.jwt_refresh_secret,
            claims={"sub": str(user.id)},
            expires_in=settings.jwt_refresh_expires_in,
        )
        response.set_cookie(
            "refresh_token", refresh_token,
            max_age=max_age(settings.jwt_refresh_expires_in), httponly=True,
            secure=settings.app_env == "production", samesite="lax", path="/",
        )


@router.post("/signup", status_code=201)
async def signup(body: SignUpRequest, session: DbSession) -> dict[str, str]:
    await auth_service.signup(
        session, pseudo=body.pseudo, password=body.password,
    )
    return {"message": "User created"}


@router.post("/signin")
async def signin(body: SignInRequest, session: DbSession) -> Response:
    user = await auth_service.signin(session, pseudo=body.pseudo, password=body.password)
    response = JSONResponse(content={"message": "Success"})
    _set_auth_cookies(response, user)
    return response


@router.post("/logout")
async def logout() -> Response:
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie(ACCESS_TOKEN_COOKIE, path="/")
    response.delete_cookie("refresh_token", path="/")
    return response


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser, session: DbSession) -> dict:
    user = await auth_service.me(session, current_user["id"])
    if user is None:
        raise AppError(401, "Unauthorized")
    return user
