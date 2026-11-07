from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from api.api.deps import get_current_user
from api.api.v1 import valuation_controller
from api.core.config import get_settings
from api.main import app
from api.schemas.valuation_schema import ValuationSessionType


def endpoint(path: str) -> str:
    """Build an API v1 endpoint path for a controller test."""

    return f"{get_settings().api_v1_prefix}{path}"


def test_get_item_valuation_returns_purchase_percentages():
    """Expose historical and remaining inventory purchase percentages."""

    user_id = uuid4()
    item_id = uuid4()
    calculated_at = datetime.now(UTC)
    calls = {}

    async def fake_current_user():
        """Return the authenticated user used by the request."""

        return {"id": user_id, "role": "USER", "pseudo": "test-user"}

    async def fake_get_item_valuation(**kwargs):
        """Capture valuation scope and return calculated percentages."""

        calls.update(kwargs)
        return {
            "item_id": item_id,
            "average_purchase_percent": Decimal("116.5"),
            "remaining_purchase_percent": Decimal("113.333333"),
            "calculated_at": calculated_at,
        }

    app.dependency_overrides[get_current_user] = fake_current_user
    app.dependency_overrides[valuation_controller.valuation_service_dependency] = (
        lambda: SimpleNamespace(get_item_valuation=fake_get_item_valuation)
    )
    try:
        with TestClient(app) as client:
            response = client.get(
                endpoint(f"/valuations/item/{item_id}"),
                params={"session_type": "MINING"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "item_id": str(item_id),
        "average_purchase_percent": "116.5",
        "remaining_purchase_percent": "113.333333",
        "calculated_at": calculated_at.isoformat().replace("+00:00", "Z"),
    }
    assert calls == {
        "user_id": user_id,
        "item_id": item_id,
        "session_type": ValuationSessionType.MINING,
    }


def test_get_material_lot_valuation_passes_catalogue_type():
    """Use the material-specific route and preserve the source session metadata."""

    user_id = uuid4()
    material_id = uuid4()
    lot_id = uuid4()
    origin_session_id = uuid4()
    calls = {}

    async def fake_current_user():
        """Return the authenticated user used by the request."""

        return {"id": user_id, "role": "USER", "pseudo": "test-user"}

    async def fake_get_lot_valuation(**kwargs):
        """Capture the typed route scope and return one lot valuation."""

        calls.update(kwargs)
        return {
            "item_id": material_id,
            "lots": [
                {
                    "lot_id": lot_id,
                    "origin_session_id": origin_session_id,
                    "origin_session_type": "TRANSACTION",
                    "origin_tt": Decimal(100),
                    "origin_ttc": Decimal(120),
                    "generated_sell_profit": Decimal(25),
                }
            ],
            "calculated_at": datetime.now(UTC),
        }

    app.dependency_overrides[get_current_user] = fake_current_user
    app.dependency_overrides[valuation_controller.valuation_service_dependency] = (
        lambda: SimpleNamespace(get_item_lot_valuation=fake_get_lot_valuation)
    )
    try:
        with TestClient(app) as client:
            response = client.get(endpoint(f"/valuations/material/{material_id}/lots"))
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["item_id"] == str(material_id)
    assert response.json()["lots"][0]["generated_sell_profit"] == "25"
    assert calls == {
        "user_id": user_id,
        "item_id": material_id,
        "session_type": ValuationSessionType.ALL,
        "item_type": "material",
    }


def test_get_mining_session_lot_valuation_returns_session_lots():
    """Expose all mining-origin lots grouped under their source session."""

    user_id = uuid4()
    session_id = uuid4()
    lot_id = uuid4()
    item_id = uuid4()
    calculated_at = datetime.now(UTC)
    calls = {}

    async def fake_current_user():
        """Return the authenticated user used by the request."""

        return {"id": user_id, "role": "USER", "pseudo": "test-user"}

    async def fake_get_lot_valuation(**kwargs):
        """Capture the mining session scope and return one lot."""

        calls.update(kwargs)
        return {
            "item_id": None,
            "lots": [
                {
                    "lot_id": lot_id,
                    "origin_session_id": session_id,
                    "origin_session_type": "MINING",
                    "origin_tt": Decimal(100),
                    "origin_ttc": Decimal(100),
                    "generated_sell_profit": Decimal(10),
                    "item_id": item_id,
                }
            ],
            "calculated_at": calculated_at,
        }

    app.dependency_overrides[get_current_user] = fake_current_user
    app.dependency_overrides[valuation_controller.valuation_service_dependency] = (
        lambda: SimpleNamespace(get_item_lot_valuation=fake_get_lot_valuation)
    )
    try:
        with TestClient(app) as client:
            response = client.get(endpoint(f"/valuations/mining/{session_id}/lots"))
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["session_id"] == str(session_id)
    assert response.json()["lots"][0]["lot_id"] == str(lot_id)
    assert calls == {
        "user_id": user_id,
        "item_id": None,
        "session_type": ValuationSessionType.MINING,
        "origin_session_id": session_id,
    }


def test_get_trade_item_lot_valuation_filters_transaction_origins():
    """Expose transaction-origin lots for one item through the trade route."""

    user_id = uuid4()
    item_id = uuid4()
    calculated_at = datetime.now(UTC)
    calls = {}

    async def fake_current_user():
        """Return the authenticated user used by the request."""

        return {"id": user_id, "role": "USER", "pseudo": "test-user"}

    async def fake_get_lot_valuation(**kwargs):
        """Capture the trade item scope and return an empty lot list."""

        calls.update(kwargs)
        return {
            "item_id": item_id,
            "lots": [],
            "calculated_at": calculated_at,
        }

    app.dependency_overrides[get_current_user] = fake_current_user
    app.dependency_overrides[valuation_controller.valuation_service_dependency] = (
        lambda: SimpleNamespace(get_item_lot_valuation=fake_get_lot_valuation)
    )
    try:
        with TestClient(app) as client:
            response = client.get(endpoint(f"/valuations/trade/{item_id}/lots"))
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["item_id"] == str(item_id)
    assert calls == {
        "user_id": user_id,
        "item_id": item_id,
        "session_type": ValuationSessionType.TRANSACTION,
        "item_type": None,
    }
