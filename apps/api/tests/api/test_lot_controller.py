from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from api.api.deps import get_current_user
from api.api.v1 import lot_controller
from api.core.config import get_settings
from api.db import get_session
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


def item_response_data(item_id):
    """Build the item attributes required by the lot collection response."""

    return SimpleNamespace(
        id=item_id,
        name="Test item",
        img_id=None,
        nexus_id=None,
        weight=None,
        is_untradeable=False,
        is_rare=False,
        is_active=True,
        nexus_url=None,
        description=None,
        created_at=None,
        updated_at=None,
    )


def test_create_lot_route_is_not_exposed(client):
    """Keep lot creation internal to session-line workflows."""

    test_client, _user_id = client

    response = test_client.post(endpoint("/lots"), json={})

    assert response.status_code == 405


def test_get_lots_passes_item_and_connected_user_to_service(client, monkeypatch):
    """Expose the FIFO read endpoint with the authenticated user scope."""

    test_client, user_id = client
    item_id = uuid4()
    calls = {}

    async def fake_get_fifo_lots(**kwargs):
        """Capture GET arguments and return the empty FIFO result."""

        calls.update(kwargs)
        return item_response_data(item_id), [], 0

    monkeypatch.setattr(
        lot_controller,
        "get_lot_service",
        lambda _session: SimpleNamespace(get_fifo_lots=fake_get_fifo_lots),
    )

    response = test_client.get(endpoint("/lots"), params={"item_id": str(item_id)})

    assert response.status_code == 200
    assert response.json()["item"]["id"] == str(item_id)
    assert response.json()["lots"] == []
    assert response.json()["total_quantity"] == 0
    assert calls == {"user_id": user_id, "item_id": item_id}


def test_get_lots_accepts_item_id_in_path(client, monkeypatch):
    """Support the resource-style route used by catalogue read endpoints."""

    test_client, user_id = client
    item_id = uuid4()
    calls = {}

    async def fake_get_fifo_lots(**kwargs):
        """Capture path-route arguments and return the empty FIFO result."""

        calls.update(kwargs)
        return item_response_data(item_id), [], 0

    monkeypatch.setattr(
        lot_controller,
        "get_lot_service",
        lambda _session: SimpleNamespace(get_fifo_lots=fake_get_fifo_lots),
    )

    response = test_client.get(endpoint(f"/lots/{item_id}"))

    assert response.status_code == 200
    assert response.json()["item"]["id"] == str(item_id)
    assert response.json()["lots"] == []
    assert response.json()["total_quantity"] == 0
    assert calls == {"user_id": user_id, "item_id": item_id}
