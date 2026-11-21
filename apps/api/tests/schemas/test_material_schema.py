from types import SimpleNamespace
from uuid import uuid4

from api.schemas import MaterialDetailsResponse


def test_material_details_serializes_material_type_object():
    """Serialize the material type as a Pydantic object with its ID and name."""

    material_type_id = uuid4()
    details = SimpleNamespace(
        material_type=SimpleNamespace(
            id=material_type_id,
            name="Natural Material",
        ),
    )

    response = MaterialDetailsResponse.model_validate(details)

    assert response.model_dump() == {
        "type": {
            "id": material_type_id,
            "name": "Natural Material",
        },
    }
