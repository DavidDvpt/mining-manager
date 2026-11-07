from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from api.core.exceptions import AppError, UnprocessingError
from api.db.models import (
    LotKind,
    SessionTransactionStatus,
    SessionTransactionType,
    SessionTransactionTypeDetail,
)
from api.services.session_transaction_service import SessionTransactionService


class TransactionContext:
    """Provide the async transaction protocol used by service unit tests."""

    async def __aenter__(self):
        """Enter the fake transaction without changing test state."""

        return self

    async def __aexit__(self, _exc_type, _exc_value, _traceback):
        """Leave the fake transaction and propagate any exception."""

        return False


@pytest.fixture
def service():
    """Build a transaction service with isolated dependency doubles."""

    session = MagicMock()
    session.begin.return_value = TransactionContext()
    session.begin_nested.return_value = TransactionContext()
    session.in_transaction.return_value = False
    repository = AsyncMock()
    item_service = AsyncMock()
    lot_service = AsyncMock()
    return SessionTransactionService(session, repository, item_service, lot_service)


def transaction_session(transaction_type, status):
    """Build the session shape returned by transaction repository methods."""

    transaction = SimpleNamespace(type=transaction_type, status=status)
    return SimpleNamespace(id=uuid4(), transaction=transaction)


async def test_create_buy_stackable_calculates_tt_and_creates_material_lot(service):
    """Create a stackable BUY with economy TT multiplied by its quantity."""

    item_id = uuid4()
    user_id = uuid4()
    line = SimpleNamespace(id=uuid4())
    expected = transaction_session(
        SessionTransactionType.BUY, SessionTransactionStatus.SOLDED
    )
    service._item_service.is_item_stackable.return_value = True
    service._item_service.get_item_with_economy.return_value = SimpleNamespace(
        economy=SimpleNamespace(tt=Decimal("1.25"))
    )
    service._repository.create_buy.return_value = (expected, line)

    result = await service.create_buy_stackable(
        user_id=user_id,
        quantity=4,
        item_id=item_id,
        kind="material",
        fee=Decimal("0.50"),
        ttc=Decimal("5.50"),
        type_detail=SessionTransactionTypeDetail.TT,
    )

    assert result is expected
    service._repository.create_buy.assert_awaited_once_with(
        user_id=user_id,
        item_id=item_id,
        lot_id=None,
        quantity=4,
        tt=Decimal("5.00"),
        fee=Decimal("0.50"),
        ttc=Decimal("5.50"),
        type_detail=SessionTransactionTypeDetail.TT,
    )
    service._lot_service.create_transaction_lot.assert_awaited_once_with(
        user_id=user_id,
        session_line=line,
        kind=LotKind.MATERIAL,
        quantity=4,
        tt=Decimal("5.00"),
    )


@pytest.mark.parametrize(
    ("quantity", "stackable", "message"),
    [
        (0, True, "Quantity must be at least 1"),
        (1, False, "Item is not stackable"),
    ],
)
async def test_create_buy_stackable_rejects_invalid_payload(
    service, quantity, stackable, message
):
    """Reject invalid quantity or an item that cannot be stacked."""

    service._item_service.is_item_stackable.return_value = stackable

    with pytest.raises(UnprocessingError, match=message):
        await service.create_buy_stackable(
            user_id=uuid4(),
            quantity=quantity,
            item_id=uuid4(),
            kind="material",
            fee=None,
            ttc=Decimal("1"),
            type_detail=SessionTransactionTypeDetail.GIFT,
        )

    service._repository.create_buy.assert_not_awaited()


async def test_create_buy_stackable_rejects_missing_item_and_tt(service):
    """Return not-found for an unknown item and conflict for missing TT."""

    item_id = uuid4()
    service._item_service.is_item_stackable.return_value = None
    with pytest.raises(AppError, match="Item not found"):
        await service.create_buy_stackable(
            user_id=uuid4(), quantity=1, item_id=item_id, kind="material",
            fee=None, ttc=Decimal("1"), type_detail=SessionTransactionTypeDetail.TT,
        )

    service._item_service.is_item_stackable.return_value = True
    service._item_service.get_item_with_economy.return_value = SimpleNamespace(
        economy=SimpleNamespace(tt=None)
    )
    with pytest.raises(UnprocessingError, match="no TT value"):
        await service.create_buy_stackable(
            user_id=uuid4(), quantity=1, item_id=item_id, kind="material",
            fee=None, ttc=Decimal("1"), type_detail=SessionTransactionTypeDetail.TT,
        )


async def test_create_buy_unstackable_persists_one_lot(service):
    """Create a non-stackable BUY with one produced lot and the supplied TT."""

    user_id = uuid4()
    item_id = uuid4()
    line = SimpleNamespace(id=uuid4())
    expected = transaction_session(
        SessionTransactionType.BUY, SessionTransactionStatus.SOLDED
    )
    service._item_service.is_item_stackable.return_value = False
    service._repository.create_buy.return_value = (expected, line)

    result = await service.create_buy_unstackable(
        user_id=user_id,
        item_id=item_id,
        kind="tool",
        tt=Decimal("12.345"),
        fee=None,
        ttc=Decimal("15"),
        type_detail=SessionTransactionTypeDetail.AUCTION,
    )

    assert result is expected
    service._repository.create_buy.assert_awaited_once_with(
        user_id=user_id, item_id=item_id, lot_id=None, quantity=1,
        tt=Decimal("12.345"), fee=None, ttc=Decimal("15"),
        type_detail=SessionTransactionTypeDetail.AUCTION,
    )
    service._lot_service.create_transaction_lot.assert_awaited_once_with(
        user_id=user_id, session_line=line, kind=LotKind.TOOL, quantity=1,
        tt=Decimal("12.345"),
    )


async def test_create_sell_stackable_allocates_fifo_lots(service):
    """Reserve the requested stackable quantity across FIFO lots."""

    first = SimpleNamespace(id=uuid4(), qty=3, reserved=0)
    second = SimpleNamespace(id=uuid4(), qty=5, reserved=1)
    item_id = uuid4()
    user_id = uuid4()
    expected = transaction_session(
        SessionTransactionType.SELL, SessionTransactionStatus.RUNNING
    )
    service._item_service.is_item_stackable.return_value = True
    service._lot_service.get_fifo_lots.return_value = (
        SimpleNamespace(id=item_id), [first, second], 7
    )
    service._lot_service.allocate_fifo_quantity.return_value = [(first, 3), (second, 3)]
    service._repository.create_sell.return_value = (expected, [])

    result = await service.create_sell_stackable(
        user_id=user_id, item_id=item_id, quantity=6,
        tt=Decimal("12"), ttc=Decimal("13"),
    )

    assert result is expected
    service._lot_service.reserve_for_sale.assert_awaited_once_with(
        lots=[(first, 3), (second, 3)]
    )
    service._repository.create_sell.assert_awaited_once_with(
        user_id=user_id,
        lines=[
            {"lot_id": first.id, "quantity": 3, "tt": Decimal("6"), "ttc": Decimal("13")},
            {"lot_id": second.id, "quantity": 3, "tt": Decimal("6"), "ttc": Decimal("13")},
        ],
    )


async def test_create_sell_stackable_rejects_insufficient_stock(service):
    """Reject a sale when available stock is not strictly greater than quantity."""

    service._item_service.is_item_stackable.return_value = True
    service._lot_service.get_fifo_lots.return_value = (SimpleNamespace(), [], 3)

    with pytest.raises(UnprocessingError, match="Insufficient"):
        await service.create_sell_stackable(
            user_id=uuid4(), item_id=uuid4(), quantity=3,
            tt=Decimal("1"), ttc=Decimal("1"),
        )

    service._repository.create_sell.assert_not_awaited()


async def test_create_sell_unstackable_reserves_lot(service):
    """Reserve one active unstackable lot before creating the SELL session."""

    lot_id = uuid4()
    user_id = uuid4()
    lot = SimpleNamespace(
        id=lot_id, is_active=True, qty=1, tool_lot=SimpleNamespace(tt=Decimal("10"))
    )
    expected = transaction_session(
        SessionTransactionType.SELL, SessionTransactionStatus.RUNNING
    )
    service._lot_service.get_unstackable_lot.return_value = lot
    service._repository.create_sell.return_value = (expected, [])

    result = await service.create_sell_unstackable(
        user_id=user_id, lot_id=lot_id, tt=Decimal("2"), ttc=Decimal("3")
    )

    assert result is expected
    service._lot_service.reserve_unstackable_for_sale.assert_awaited_once_with(lot=lot)
    service._repository.create_sell.assert_awaited_once_with(
        user_id=user_id,
        lines=[{"lot_id": lot_id, "quantity": 1, "tt": Decimal("2"), "ttc": Decimal("3")}],
    )


async def test_create_sell_unstackable_rejects_limited_lot_with_zero_tt(service):
    """Reject a limited tool sale without a positive TT value."""

    lot = SimpleNamespace(
        id=uuid4(),
        is_active=True,
        qty=1,
        origin=SimpleNamespace(item=SimpleNamespace(name="Test Tool (L)")),
        tool_lot=SimpleNamespace(tt=Decimal("10")),
    )
    service._lot_service.get_unstackable_lot.return_value = lot

    with pytest.raises(UnprocessingError, match="greater than 0"):
        await service.create_sell_unstackable(
            user_id=uuid4(), lot_id=lot.id, tt=Decimal("0"), ttc=Decimal("1")
        )

    service._lot_service.reserve_unstackable_for_sale.assert_not_awaited()


async def test_create_consumed_material_consumes_fifo_with_zero_fee(service):
    """Consume material FIFO and persist TTC equal to TT with no fee."""

    user_id = uuid4()
    item_id = uuid4()
    first = SimpleNamespace(id=uuid4(), qty=3, reserved=0)
    second = SimpleNamespace(id=uuid4(), qty=5, reserved=0)
    expected = transaction_session(
        SessionTransactionType.CONSUMED, SessionTransactionStatus.SOLDED
    )
    service._item_service.is_item_material.return_value = True
    service._item_service.get_item_with_economy.return_value = SimpleNamespace(
        economy=SimpleNamespace(tt=Decimal("1.25"))
    )
    service._lot_service.get_fifo_lots.return_value = (
        SimpleNamespace(id=item_id), [first, second], 8
    )
    service._lot_service.allocate_fifo_quantity.return_value = [(first, 3), (second, 1)]
    service._repository.create_consumed.return_value = (expected, [])

    result = await service.create_consumed_material(
        user_id=user_id, item_id=item_id, quantity=4
    )

    assert result is expected
    service._lot_service.consume_for_consumption.assert_awaited_once_with(
        lots=[(first, 3), (second, 1)]
    )
    service._repository.create_consumed.assert_awaited_once_with(
        user_id=user_id,
        lines=[
            {"lot_id": first.id, "quantity": 3, "tt": Decimal("3.75"), "ttc": Decimal("3.75")},
            {"lot_id": second.id, "quantity": 1, "tt": Decimal("1.25"), "ttc": Decimal("1.25")},
        ],
    )


@pytest.mark.parametrize(
    ("material", "total_quantity", "message"),
    [
        (False, 10, "Only material"),
        (True, 2, "Insufficient"),
    ],
)
async def test_create_consumed_material_rejects_non_material_or_insufficient_stock(
    service, material, total_quantity, message
):
    """Reject consumption for non-material items or unavailable stock."""

    service._item_service.is_item_material.return_value = material
    service._item_service.get_item_with_economy.return_value = SimpleNamespace(
        economy=SimpleNamespace(tt=Decimal("1"))
    )
    service._lot_service.get_fifo_lots.return_value = (SimpleNamespace(), [], total_quantity)

    with pytest.raises(UnprocessingError, match=message):
        await service.create_consumed_material(
            user_id=uuid4(), item_id=uuid4(), quantity=3
        )

    service._repository.create_consumed.assert_not_awaited()


async def test_patch_status_settles_each_line_and_persists_status(service):
    """Settle all reserved lots and persist SOLD status for an owned SELL."""

    user_id = uuid4()
    session_id = uuid4()
    lot_id = uuid4()
    transaction = SimpleNamespace(
        session_id=session_id,
        type=SessionTransactionType.SELL,
        status=SessionTransactionStatus.RUNNING,
        session=SimpleNamespace(lines=[SimpleNamespace(lot_id=lot_id, qty=2)]),
    )
    service._repository.get_transaction_by_id.return_value = transaction
    lot = SimpleNamespace(id=lot_id)
    service._lot_service.get_lot_by_id.return_value = lot

    result = await service.patch_status(
        user_id=user_id, session_id=session_id,
        status=SessionTransactionStatus.SOLDED,
    )

    assert result is transaction
    service._lot_service.settle_sale_lot.assert_awaited_once_with(
        lot=lot, quantity=2, sold=True
    )
    service._repository.patch_status.assert_awaited_once_with(
        transaction=transaction, status=SessionTransactionStatus.SOLDED
    )


@pytest.mark.parametrize(
    ("transaction_type", "status", "message"),
    [
        (SessionTransactionType.BUY, SessionTransactionStatus.SOLDED, "Only SELL"),
        (SessionTransactionType.SELL, SessionTransactionStatus.CANCELLED, "Only RUNNING"),
    ],
)
async def test_patch_status_rejects_invalid_transaction_state(
    service, transaction_type, status, message
):
    """Reject status changes outside a running owned SELL transaction."""

    transaction = SimpleNamespace(
        type=transaction_type,
        status=status,
        session=SimpleNamespace(lines=[]),
    )
    service._repository.get_transaction_by_id.return_value = transaction

    with pytest.raises(UnprocessingError, match=message):
        await service.patch_status(
            user_id=uuid4(), session_id=uuid4(), status=SessionTransactionStatus.RETURNED
        )

    service._repository.patch_status.assert_not_awaited()


async def test_get_transaction_by_id_scopes_lookup_and_maps_missing(service):
    """Return an owned transaction and map an absent transaction to 404."""

    user_id = uuid4()
    session_id = uuid4()
    expected = SimpleNamespace(id=uuid4())
    service._repository.get_transaction_by_id.return_value = expected
    assert await service.get_transaction_by_id(user_id=user_id, session_id=session_id) is expected
    service._repository.get_transaction_by_id.assert_awaited_once_with(
        session_id=session_id, user_id=user_id
    )

    service._repository.get_transaction_by_id.return_value = None
    with pytest.raises(AppError, match="Transaction not found"):
        await service.get_transaction_by_id(user_id=user_id, session_id=session_id)
