from types import SimpleNamespace
from uuid import uuid4

import pytest
from api.api.deps import get_current_user
from api.api.v1.auth_controller import ACCESS_TOKEN_COOKIE
from api.core.config import get_settings
from api.db import get_session
from api.main import app, public_openapi_schema
from api.services import auth_service
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    async def fake_session():
        yield object()

    app.dependency_overrides[get_session] = fake_session
    with TestClient(app) as test_client:
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
