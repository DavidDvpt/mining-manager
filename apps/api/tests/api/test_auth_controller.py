import time
from types import SimpleNamespace
from uuid import uuid4

import jwt
import pytest
from api.api.deps import (
    ACCESS_TOKEN_COOKIE,
    REFRESH_TOKEN_COOKIE,
    get_current_user,
)
from api.core.config import get_settings
from api.core.exceptions import AppError
from api.db import get_session
from api.main import app, public_openapi_schema
from api.services import auth_service
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


@pytest.fixture
def client():
    async def fake_session():
        yield object()

    app.dependency_overrides[get_session] = fake_session
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def endpoint(path: str) -> str:
    return f"{get_settings().api_v1_prefix}{path}"


def test_signup_delegates_to_auth_service(client, monkeypatch):
    calls = {}

    async def fake_signup(session, **kwargs):
        calls["session"] = session
        calls["kwargs"] = kwargs

    monkeypatch.setattr(auth_service, "signup", fake_signup)

    response = client.post(
        endpoint("/signup"),
        json={
            "pseudo": "test-user",
            "password": "password123",
        },
    )

    assert response.status_code == 201
    assert response.json() == {"message": "User created"}
    assert calls["kwargs"] == {
        "pseudo": "test-user",
        "password": "password123",
    }


def test_signup_returns_conflict_when_database_rejects_duplicate_user(client, monkeypatch):
    async def fake_signup(session, **kwargs):
        raise IntegrityError(
            "INSERT INTO user",
            {},
            SimpleNamespace(sqlstate="23505"),
        )

    monkeypatch.setattr(auth_service, "signup", fake_signup)

    response = client.post(
        endpoint("/signup"),
        json={"pseudo": "test-user", "password": "password123"},
    )

    assert response.status_code == 409
    assert response.json() == {"message": "Resource already exists"}


def test_signup_rejects_profile_fields(client):
    response = client.post(
        endpoint("/signup"),
        json={
            "pseudo": "test-user",
            "password": "password123",
            "email": "test@example.com",
        },
    )

    assert response.status_code == 422


def test_signin_returns_access_cookie(client, monkeypatch):
    user = SimpleNamespace(
        id=uuid4(),
        role=SimpleNamespace(value="USER"),
        pseudo="test-user",
    )

    async def fake_signin(session, *, pseudo, password):
        assert pseudo == "test-user"
        assert password == "password123"
        return user

    monkeypatch.setattr(auth_service, "signin", fake_signin)

    response = client.post(
        endpoint("/signin"),
        json={"pseudo": "test-user", "password": "password123"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Success"}
    assert response.cookies.get(ACCESS_TOKEN_COOKIE)


def test_signin_returns_unauthorized_for_invalid_credentials(client, monkeypatch):
    async def fake_signin(session, *, pseudo, password):
        raise AppError(401, "Identifiants invalides")

    monkeypatch.setattr(auth_service, "signin", fake_signin)

    response = client.post(
        endpoint("/signin"),
        json={"pseudo": "test-user", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json() == {"message": "Identifiants invalides"}


def test_signin_returns_internal_error_when_database_fails(client, monkeypatch):
    async def fake_signin(session, *, pseudo, password):
        raise SQLAlchemyError("database unavailable")

    monkeypatch.setattr(auth_service, "signin", fake_signin)

    response = client.post(
        endpoint("/signin"),
        json={"pseudo": "test-user", "password": "password123"},
    )

    assert response.status_code == 500
    assert response.json() == {"message": "Internal server error"}


def test_refresh_token_rotates_cookies_and_marks_access_token(client, monkeypatch):
    user_id = uuid4()
    refresh_token = jwt.encode(
        {
            "sub": str(user_id),
            "token_type": "refresh",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
        },
        get_settings().jwt_refresh_secret,
        algorithm="HS256",
    )

    async def fake_get_by_id(repository, current_user_id):
        assert current_user_id == user_id
        return SimpleNamespace(
            id=user_id,
            role=SimpleNamespace(value="USER"),
            pseudo="test-user",
            is_active=True,
        )

    monkeypatch.setattr(auth_service.UserRepository, "get_by_id", fake_get_by_id)
    client.cookies.set(REFRESH_TOKEN_COOKIE, refresh_token)

    response = client.post(endpoint("/refresh-token"))

    assert response.status_code == 200
    assert response.cookies.get(ACCESS_TOKEN_COOKIE)
    assert response.cookies.get(REFRESH_TOKEN_COOKIE)
    access_payload = jwt.decode(
        response.cookies.get(ACCESS_TOKEN_COOKIE),
        get_settings().jwt_access_secret,
        algorithms=["HS256"],
    )
    assert access_payload["token_type"] == "access"
    assert access_payload["issued_from"] == "refresh"


def test_refresh_token_expires_after_one_hour_of_inactivity(client):
    now = int(time.time())
    refresh_token = jwt.encode(
        {
            "sub": str(uuid4()),
            "token_type": "refresh",
            "iat": now - 3601,
            "exp": now + 3600,
        },
        get_settings().jwt_refresh_secret,
        algorithm="HS256",
    )
    client.cookies.set(REFRESH_TOKEN_COOKIE, refresh_token)

    response = client.post(endpoint("/refresh-token"))

    assert response.status_code == 401
    assert response.json() == {"message": "Session expired"}
    assert any(
        f"{ACCESS_TOKEN_COOKIE}=\"\"" in value
        for value in response.headers.get_list("set-cookie")
    )


def test_refresh_token_returns_internal_error_when_database_fails(client, monkeypatch):
    now = int(time.time())
    refresh_token = jwt.encode(
        {
            "sub": str(uuid4()),
            "token_type": "refresh",
            "iat": now,
            "exp": now + 3600,
        },
        get_settings().jwt_refresh_secret,
        algorithm="HS256",
    )

    async def fake_get_by_id(repository, user_id):
        raise SQLAlchemyError("database unavailable")

    monkeypatch.setattr(auth_service.UserRepository, "get_by_id", fake_get_by_id)
    client.cookies.set(REFRESH_TOKEN_COOKIE, refresh_token)

    response = client.post(endpoint("/refresh-token"))

    assert response.status_code == 500
    assert response.json() == {"message": "Internal server error"}


def test_me_returns_authenticated_user(client, monkeypatch):
    user_id = uuid4()

    async def fake_me(session, current_user_id):
        assert current_user_id == user_id
        return {"id": str(user_id), "role": "USER", "pseudo": "test-user"}

    async def fake_current_user():
        return {"id": user_id, "role": "USER", "pseudo": "test-user"}

    app.dependency_overrides[get_current_user] = fake_current_user
    monkeypatch.setattr(auth_service, "me", fake_me)

    response = client.get(endpoint("/me"))

    assert response.status_code == 200
    assert response.json() == {
        "id": str(user_id),
        "role": "USER",
        "pseudo": "test-user",
    }


def test_me_requires_authentication(client):
    response = client.get(endpoint("/me"))

    assert response.status_code == 401
    assert response.json() == {"message": "Unauthorized"}


def test_logout_deletes_auth_cookies(client):
    response = client.post(endpoint("/logout"))

    assert response.status_code == 200
    assert response.json() == {"message": "Logged out"}
    set_cookie = response.headers.get_list("set-cookie")
    assert any(f"{ACCESS_TOKEN_COOKIE}=\"\"" in value for value in set_cookie)
    assert any('refresh_token=""' in value for value in set_cookie)


def test_full_openapi_includes_auth_but_interactive_docs_hide_it():
    full_paths = app.openapi()["paths"]
    public_paths = public_openapi_schema(app)["paths"]

    assert f"{get_settings().api_v1_prefix}/me" in full_paths
    assert f"{get_settings().api_v1_prefix}/profile" in full_paths
    assert f"{get_settings().api_v1_prefix}/me" not in public_paths
    assert f"{get_settings().api_v1_prefix}/profile" not in public_paths
    assert f"{get_settings().api_v1_prefix}/enhancers" in public_paths
