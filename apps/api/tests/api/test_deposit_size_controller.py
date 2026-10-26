from decimal import Decimal
from uuid import UUID

from api.api.v1.deposit_size_controller import get_deposit_size_service
from api.core.config import get_settings
from api.main import app
from fastapi.testclient import TestClient


def endpoint(path: str) -> str:
    return f"{get_settings().api_v1_prefix}{path}"


def test_get_all_deposit_sizes_is_public():
    class FakeService:
        async def get_all(self):
            return [
                {
                    "id": UUID("00000000-0000-0000-0000-000000000001"),
                    "size": 1,
                    "roman_size": "I",
                    "size_label": "Minimal",
                    "min": Decimal("0.05"),
                    "max": Decimal("0.24"),
                }
            ]

    app.dependency_overrides[get_deposit_size_service] = lambda: FakeService()
    try:
        with TestClient(app) as client:
            response = client.get(endpoint("/mining/deposit_sizes"))
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "00000000-0000-0000-0000-000000000001",
            "size": 1,
            "romanSize": "I",
            "sizeLabel": "Minimal",
            "min": "0.05",
            "max": "0.24",
        }
    ]


def test_deposit_sizes_are_visible_in_openapi():
    paths = app.openapi()["paths"]

    assert f"{get_settings().api_v1_prefix}/mining/deposit_sizes" in paths
