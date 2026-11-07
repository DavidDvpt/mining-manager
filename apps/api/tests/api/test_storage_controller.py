from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from api.api.deps import get_current_user
from api.api.v1 import storage_controller
from api.core.config import get_settings
from api.main import app


def endpoint(path: str) -> str:
    """Build an API v1 endpoint path for a controller test."""

    return f"{get_settings().api_v1_prefix}{path}"


def test_get_material_stock_returns_compact_aggregated_quantities(monkeypatch):
    """Expose material stock as a material ID to quantity mapping."""

    user_id = uuid4()
    first_material_id = uuid4()
    second_material_id = uuid4()
    calls = {}

    async def fake_current_user():
        """Return the authenticated user used by the request."""

        return {"id": user_id, "role": "USER", "pseudo": "test-user"}

    async def fake_get_material_stock(**kwargs):
        """Capture the user scope and return compact stock data."""

        calls.update(kwargs)
        return {first_material_id: 12, second_material_id: 3}

    app.dependency_overrides[get_current_user] = fake_current_user
    app.dependency_overrides[storage_controller.storage_service_dependency] = (
        lambda: SimpleNamespace(get_material_stock=fake_get_material_stock)
    )
    try:
        with TestClient(app) as client:
            response = client.get(endpoint("/storage/material/stock"))
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        str(first_material_id): 12,
        str(second_material_id): 3,
    }
    assert calls == {"user_id": user_id}


def test_get_material_stock_for_item_returns_one_material_mapping():
    """Expose the scalar material stock endpoint with the compact response."""

    user_id = uuid4()
    material_id = uuid4()
    calls = {}

    async def fake_current_user():
        """Return the authenticated user used by the request."""

        return {"id": user_id, "role": "USER", "pseudo": "test-user"}

    async def fake_get_material_stock_for_item(**kwargs):
        """Capture the user and material scope passed by the controller."""

        calls.update(kwargs)
        return {material_id: 9}

    app.dependency_overrides[get_current_user] = fake_current_user
    app.dependency_overrides[storage_controller.storage_service_dependency] = (
        lambda: SimpleNamespace(
            get_material_stock_for_item=fake_get_material_stock_for_item
        )
    )
    try:
        with TestClient(app) as client:
            response = client.get(
                endpoint(f"/storage/material/{material_id}/stock")
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {str(material_id): 9}
    assert calls == {"user_id": user_id, "material_id": material_id}
