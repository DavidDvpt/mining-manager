from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

from api.services.storage_service import StorageService


async def test_get_material_stock_delegates_to_one_grouped_lot_query():
    """Return grouped material stock from the lot service in one call."""

    first_material_id = uuid4()
    second_material_id = uuid4()
    lot_service = SimpleNamespace(
        get_available_quantities=AsyncMock(
            return_value={first_material_id: 8, second_material_id: 3}
        )
    )
    material_service = SimpleNamespace(
        get_all=AsyncMock(
            return_value=[
                SimpleNamespace(id=first_material_id),
                SimpleNamespace(id=second_material_id),
            ]
        )
    )
    service = StorageService(lot_service, material_service)
    user_id = uuid4()

    stock = await service.get_material_stock(user_id=user_id)

    assert stock == {first_material_id: 8, second_material_id: 3}
    lot_service.get_available_quantities.assert_awaited_once_with(
        user_id=user_id,
        item_ids={first_material_id, second_material_id},
    )


async def test_get_material_stock_for_item_delegates_to_one_scalar_lot_query():
    """Return one material quantity without querying other material items."""

    material_id = uuid4()
    user_id = uuid4()
    lot_service = SimpleNamespace(
        get_available_quantities=AsyncMock(return_value={material_id: 7})
    )
    material_service = SimpleNamespace(
        get_by_id=AsyncMock(return_value=SimpleNamespace(id=material_id))
    )
    service = StorageService(lot_service, material_service)

    stock = await service.get_material_stock_for_item(
        user_id=user_id,
        material_id=material_id,
    )

    assert stock == {material_id: 7}
    material_service.get_by_id.assert_awaited_once_with(material_id)
    lot_service.get_available_quantities.assert_awaited_once_with(
        user_id=user_id,
        item_ids={material_id},
    )
