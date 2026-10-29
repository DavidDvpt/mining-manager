from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from api.api.deps import get_current_user
from api.api.v1 import lot_controller
from api.core.config import get_settings
from api.db import get_session
from api.db.models import LotKind
from api.main import app


@pytest.fixture
def client(monkeypatch):
    """Return an API client with authenticated-user and DB dependencies mocked."""

    user_id = uuid4()

    async def fake_session():
        """Yield a fake database session for controller tests."""

        yield object()

    async def fake_current_user():
        """Return the authenticated user used by the request."""

        return {"id": user_id, "role": "USER", "pseudo": "test-user"}

    app.dependency_overrides[get_session] = fake_session
    app.dependency_overrides[get_current_user] = fake_current_user
    with TestClient(app) as test_client:
        yield test_client, user_id
    app.dependency_overrides.clear()


def endpoint(path: str) -> str:
    """Build an API v1 endpoint path for a controller test."""

    return f"{get_settings().api_v1_prefix}{path}"


def test_create_lot_returns_only_the_created_id(client, monkeypatch):
    """Return the minimal lot response and pass the connected user id."""

    test_client, user_id = client
    line_id = uuid4()
    lot_id = uuid4()
    calls = {}

    async def fake_create_lot(session, **kwargs):
        """Capture service arguments and return a fake created lot."""

        calls.update(kwargs)
        return SimpleNamespace(id=lot_id)

    monkeypatch.setattr(lot_controller, "create_lot", fake_create_lot)

    response = test_client.post(
        endpoint("/lots"),
        json={
            "kind": LotKind.MATERIAL.value,
            "session_line_id": str(line_id),
            "quantity": 4,
        },
    )

    assert response.status_code == 201
    assert response.json() == {"id": str(lot_id)}
    assert calls["user_id"] == user_id
    assert calls["session_line_id"] == line_id


def test_create_lot_rejects_unknown_payload_fields(client):
    """Reject fields outside the create-lot contract."""

    test_client, _user_id = client

    response = test_client.post(
        endpoint("/lots"),
        json={
            "kind": "MATERIAL",
            "session_line_id": str(uuid4()),
            "quantity": 1,
            "status": "ACTIVE",
        },
    )

    assert response.status_code == 422
