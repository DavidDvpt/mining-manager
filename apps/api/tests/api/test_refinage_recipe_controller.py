from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from api.api.v1 import refinage_recipe_controller
from api.core.config import get_settings
from api.main import app


def endpoint(path: str) -> str:
    """Build an API v1 endpoint path for a controller test."""

    return f"{get_settings().api_v1_prefix}{path}"


def test_get_recipes_by_origin_returns_recipe_collection(monkeypatch):
    """Expose all recipes returned for the requested origin material."""

    origin_id = uuid4()
    result_id = uuid4()
    recipe = SimpleNamespace(
        id=uuid4(),
        result=result_id,
        origin=origin_id,
        quantity=3,
    )
    calls = {}

    async def fake_get_by_origin(received_origin_id):
        """Capture the origin identifier passed by the controller."""

        calls["origin_id"] = received_origin_id
        return [recipe]

    app.dependency_overrides[refinage_recipe_controller.get_refinage_recipe_service] = (
        lambda: SimpleNamespace(get_by_origin=fake_get_by_origin)
    )
    try:
        with TestClient(app) as client:
            response = client.get(endpoint(f"/refinage/recipe/{origin_id}"))
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(recipe.id),
            "result": str(result_id),
            "origin": str(origin_id),
            "quantity": 3,
        }
    ]
    assert calls == {"origin_id": origin_id}
