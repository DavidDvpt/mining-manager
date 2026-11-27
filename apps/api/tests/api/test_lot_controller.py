from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from api.api.deps import get_current_user
from api.api.v1 import lot_controller
from api.core.config import get_settings
from api.db import get_session
from api.db.models import Lot, LotType, Session, SessionLine, SessionLineType
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
    assert response.json()["totalQuantity"] == 0
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
    assert response.json()["totalQuantity"] == 0
    assert calls == {"user_id": user_id, "item_id": item_id}


@pytest.mark.parametrize("use_path", [True, False])
@pytest.mark.parametrize("quantity", [12, 0, None])
def test_get_lots_serializes_origin_quantity(client, monkeypatch, use_path, quantity):
    """Return ORM origin quantity as qty, preserving zero and null on both routes."""

    test_client, user_id = client
    item_id = uuid4()
    item = item_response_data(item_id)
    origin = SessionLine(
        id=uuid4(),
        session_id=uuid4(),
        item_id=item_id,
        type=SessionLineType.PRODUCED,
        lot_id=None,
        quantity=quantity,
        session=Session(
            id=uuid4(),
            user_id=user_id,
            started_at=datetime.now(UTC).date(),
            ended_at=None,
        ),
    )
    lot = Lot(
        id=uuid4(),
        user_id=user_id,
        type=LotType.TRANSACTION,
        origin_id=str(origin.id),
        origin=origin,
        qty=5,
        reserved=0,
        created_at=datetime.now(UTC),
        updated_at=None,
        is_active=True,
    )

    async def fake_get_fifo_lots(**kwargs):
        """Return a populated FIFO lot with its ORM session-line origin."""

        return item, [lot], lot.qty

    monkeypatch.setattr(
        lot_controller,
        "get_lot_service",
        lambda _session: SimpleNamespace(get_fifo_lots=fake_get_fifo_lots),
    )

    response = test_client.get(
        endpoint(f"/lots/{item_id}" if use_path else "/lots"),
        params=None if use_path else {"item_id": str(item_id)},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["totalQuantity"] == 5
    assert data["lots"][0]["qty"] == 5
    assert data["lots"][0]["origin"]["qty"] == quantity
    assert "quantity" not in data["lots"][0]["origin"]


def test_get_unstackable_lot_returns_item_and_tool_attributes(client, monkeypatch):
    """Expose an owned unstackable lot with its tool tier and TT."""

    test_client, user_id = client
    lot_id = uuid4()
    item_id = uuid4()
    item = item_response_data(item_id)
    lot = SimpleNamespace(
        id=lot_id,
        user_id=user_id,
        type=SimpleNamespace(value="TRANSACTION"),
        origin=SimpleNamespace(item=item),
        qty=1,
        reserved=0,
        tool_lot=SimpleNamespace(tier=7, tt="12.34500"),
        created_at=datetime.now(UTC),
        updated_at=None,
        is_active=True,
    )
    calls = {}

    async def fake_get_unstackable_lot(**kwargs):
        """Capture unstackable-lot lookup arguments and return the test lot."""

        calls.update(kwargs)
        return lot

    monkeypatch.setattr(
        lot_controller,
        "get_lot_service",
        lambda _session: SimpleNamespace(
            get_unstackable_lot=fake_get_unstackable_lot
        ),
    )

    response = test_client.get(endpoint(f"/lots/unstackable/{lot_id}"))

    assert response.status_code == 200
    assert response.json()["id"] == str(lot_id)
    assert response.json()["item"]["id"] == str(item_id)
    assert response.json()["tier"] == 7
    assert response.json()["tt"] == "12.34500"
    assert calls == {"user_id": user_id, "lot_id": lot_id}
