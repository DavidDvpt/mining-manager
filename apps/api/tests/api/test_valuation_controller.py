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
