from unittest.mock import AsyncMock
from uuid import uuid4

from api.services.enhancer_service import EnhancerService


async def test_get_stock_by_type_socket_delegates_ids_to_lot_service():
    """Resolve enhancer IDs first, then aggregate their stock in one call."""

    first_id = uuid4()
    second_id = uuid4()
    repository = AsyncMock()
    repository.get_item_ids_by_type_socket.return_value = [first_id, second_id]
    lot_service = AsyncMock()
    lot_service.get_available_quantities.return_value = {
        first_id: 4,
        second_id: 3,
    }
    service = EnhancerService(repository, lot_service)
    user_id = uuid4()

    stock = await service.get_stock_by_type_socket(
        user_id=user_id,
        enhancer_type="SPEED",
        socket=2,
    )

    assert stock == 7
    repository.get_item_ids_by_type_socket.assert_awaited_once_with(
        enhancer_type="SPEED",
        socket=2,
    )
    lot_service.get_available_quantities.assert_awaited_once_with(
        user_id=user_id,
        item_ids=[first_id, second_id],
    )
