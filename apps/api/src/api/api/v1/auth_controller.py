"""Public sign-in/sign-up and cookie-authenticated identity endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import ACCESS_TOKEN_COOKIE, REFRESH_TOKEN_COOKIE, CurrentUser
from api.core.config import get_settings
from api.core.exceptions import AppError
from api.db import get_session
from api.schemas.auth_schema import SignInRequest, SignUpRequest, UserResponse
from api.services import auth_service

router = APIRouter(tags=["auth"])
DbSession = Annotated[AsyncSession, Depends(get_session)]
def _delete_auth_cookies(response: Response) -> None:
    response.delete_cookie(ACCESS_TOKEN_COOKIE, path="/")
    response.delete_cookie(REFRESH_TOKEN_COOKIE, path="/")


def _set_auth_cookies(
    response: Response, tokens: auth_service.AuthTokens
) -> None:
    settings = get_settings()
    response.set_cookie(
        ACCESS_TOKEN_COOKIE, tokens.access_token,
        max_age=tokens.access_max_age, httponly=True,
        secure=settings.app_env == "production", samesite="lax", path="/",
    )
    if tokens.refresh_token and tokens.refresh_max_age is not None:
        response.set_cookie(
            REFRESH_TOKEN_COOKIE, tokens.refresh_token,
            max_age=tokens.refresh_max_age, httponly=True,
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
    _set_auth_cookies(
        response,
        auth_service.issue_tokens(
            user,
            access_expires_in=get_settings().jwt_access_expires_in,
            access_issued_from="signin",
        ),
    )
    return response


@router.post("/refresh-token")
async def refresh_token(request: Request, session: DbSession) -> Response:
    """Refresh authentication only while the refresh token is not idle-expired."""

    token = request.cookies.get(REFRESH_TOKEN_COOKIE)
    try:
        tokens = await auth_service.refresh_authentication(session, token)
    except AppError as error:
        response = JSONResponse(content={"message": error.message}, status_code=error.status_code)
        _delete_auth_cookies(response)
        return response

    response = JSONResponse(content={"message": "Token refreshed"})
    _set_auth_cookies(response, tokens)
    return response


@router.post("/logout")
async def logout() -> Response:
    response = JSONResponse(content={"message": "Logged out"})
    _delete_auth_cookies(response)
    return response


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser, session: DbSession) -> dict:
    user = await auth_service.me(session, current_user["id"])
    if user is None:
        raise AppError(401, "Unauthorized")
    return user
