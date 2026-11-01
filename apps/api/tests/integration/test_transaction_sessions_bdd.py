from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select

from api.db.models import (
    Economy,
    Item,
    Lot,
    Material,
    MaterialType,
    SessionLine,
    SessionLineTransaction,
    SessionTransaction,
    SessionTransactionStatus,
    SessionTransactionType,
    SessionTransactionTypeDetail,
    ToolLot,
    User,
)
from api.services.session_transaction_service import get_session_transaction_service


async def given_user_and_stackable_item(test_db_session):
    """Create an isolated user and material item with a catalogue TT value."""

    user = User(pseudo=f"transaction-{uuid4().hex[:12]}", password_hash="hash")
    item = Item(name=f"Transaction material {uuid4()}")
    material_type = MaterialType(name=f"Transaction type {uuid4()}")
    test_db_session.add_all([user, item, material_type])
    await test_db_session.flush()
    test_db_session.add_all([
        Material(item_id=item.id, type=material_type.id),
        Economy(item_id=item.id, tt=Decimal("1.25")),
    ])
    await test_db_session.commit()
    await test_db_session.close()
    return user, item


async def given_user_and_unstackable_item(test_db_session):
    """Create an isolated user and a non-material item for tool transactions."""

    user = User(pseudo=f"transaction-tool-{uuid4().hex[:12]}", password_hash="hash")
    item = Item(name=f"Transaction tool {uuid4()}")
    test_db_session.add_all([user, item])
    await test_db_session.commit()
    await test_db_session.close()
    return user, item


async def test_bdd_stackable_buy_persists_transaction_line_and_lot(test_db_session):
    """Persist a stackable BUY, its calculated TT, and its produced material lot."""

    user, item = await given_user_and_stackable_item(test_db_session)
    created = await get_session_transaction_service(test_db_session).create_buy_stackable(
        user_id=user.id,
        quantity=4,
        item_id=item.id,
        kind="material",
        fee=Decimal("0.50"),
        ttc=Decimal("5.50"),
        type_detail=SessionTransactionTypeDetail.TT,
    )

    transaction = await test_db_session.scalar(
        select(SessionTransaction).where(SessionTransaction.session_id == created.id)
    )
    line = await test_db_session.scalar(
        select(SessionLine).where(SessionLine.session_id == created.id)
    )
    line_transaction = await test_db_session.scalar(
        select(SessionLineTransaction).where(SessionLineTransaction.session_line_id == line.id)
    )
    lot = await test_db_session.scalar(select(Lot).where(Lot.origin_id == str(line.id)))

    assert transaction is not None
    assert transaction.type is SessionTransactionType.BUY
    assert transaction.status is SessionTransactionStatus.SOLDED
    assert line.item_id == item.id
    assert line.qty == 4
    assert line_transaction.tt == Decimal("5.00000")
    assert line_transaction.fee == Decimal("0.50")
    assert lot is not None
    assert lot.user_id == user.id
    assert lot.qty == 4
    assert lot.reserved == 0


async def test_bdd_stackable_sell_reserves_then_returns_fifo_stock(test_db_session):
    """Reserve stackable stock for a SELL and release it when returned."""

    user, item = await given_user_and_stackable_item(test_db_session)
    service = get_session_transaction_service(test_db_session)
    buy = await service.create_buy_stackable(
        user_id=user.id,
        quantity=10,
        item_id=item.id,
        kind="material",
        fee=None,
        ttc=Decimal("13"),
        type_detail=SessionTransactionTypeDetail.EXISTING_STOCK,
    )

    sell = await service.create_sell_stackable(
        user_id=user.id,
        item_id=item.id,
        quantity=4,
        tt=Decimal("4"),
        ttc=Decimal("4.40"),
    )
    lot = await test_db_session.scalar(
        select(Lot)
        .join(Lot.origin)
        .where(SessionLine.session_id == buy.id)
    )
    assert lot is not None
    assert lot.qty == 10
    assert lot.reserved == 4

    await service.patch_status(
        user_id=user.id,
        session_id=sell.id,
        status=SessionTransactionStatus.RETURNED,
    )
    returned = await test_db_session.scalar(
        select(SessionTransaction).where(SessionTransaction.session_id == sell.id)
    )
    lot = await test_db_session.scalar(select(Lot).where(Lot.user_id == user.id))
    assert lot.qty == 10
    assert lot.reserved == 0
    assert returned is not None
    assert returned.status is SessionTransactionStatus.RETURNED


async def test_bdd_stackable_sell_sold_consumes_reserved_stock(test_db_session):
    """Consume reserved stackable stock and deactivate an exhausted lot on SOLD."""

    user, item = await given_user_and_stackable_item(test_db_session)
    service = get_session_transaction_service(test_db_session)
    await service.create_buy_stackable(
        user_id=user.id,
        quantity=3,
        item_id=item.id,
        kind="material",
        fee=None,
        ttc=Decimal("3"),
        type_detail=SessionTransactionTypeDetail.GIFT,
    )
    sell = await service.create_sell_stackable(
        user_id=user.id,
        item_id=item.id,
        quantity=2,
        tt=Decimal("2"),
        ttc=Decimal("2"),
    )
    await service.patch_status(
        user_id=user.id,
        session_id=sell.id,
        status=SessionTransactionStatus.SOLDED,
    )

    lot = await test_db_session.scalar(select(Lot).where(Lot.user_id == user.id))
    assert lot is not None
    assert lot.qty == 1
    assert lot.reserved == 0
    assert lot.is_active is True


async def test_bdd_unstackable_tool_buy_sell_and_cancel_restores_lot(test_db_session):
    """Create, reserve, and cancel a tool transaction without consuming its lot."""

    user, item = await given_user_and_unstackable_item(test_db_session)
    service = get_session_transaction_service(test_db_session)
    buy = await service.create_buy_unstackable(
        user_id=user.id,
        item_id=item.id,
        kind="tool",
        tt=Decimal("12.345"),
        fee=None,
        ttc=Decimal("15"),
        type_detail=SessionTransactionTypeDetail.AUCTION,
    )
    buy_line = await test_db_session.scalar(
        select(SessionLine).where(SessionLine.session_id == buy.id)
    )
    assert buy_line is not None
    lot = await test_db_session.scalar(select(Lot).where(Lot.origin_id == str(buy_line.id)))
    assert lot is not None
    tool_lot = await test_db_session.scalar(select(ToolLot).where(ToolLot.lot_id == lot.id))
    assert tool_lot is not None
    assert tool_lot.tt == Decimal("12.34500")

    sell = await service.create_sell_unstackable(
        user_id=user.id, lot_id=lot.id, tt=Decimal("13"), ttc=Decimal("14")
    )
    await test_db_session.refresh(lot)
    assert lot.reserved == 1

    await service.patch_status(
        user_id=user.id,
        session_id=sell.id,
        status=SessionTransactionStatus.CANCELLED,
    )
    lot = await test_db_session.scalar(select(Lot).where(Lot.user_id == user.id))
    assert lot.qty == 1
    assert lot.reserved == 0
    assert lot.is_active is True


async def test_bdd_consumed_material_consumes_stock_and_records_zero_fee(
    test_db_session,
):
    """Consume material stock and persist matching TT/TTC with a zero fee."""

    user, item = await given_user_and_stackable_item(test_db_session)
    service = get_session_transaction_service(test_db_session)
    await service.create_buy_stackable(
        user_id=user.id,
        quantity=5,
        item_id=item.id,
        kind="material",
        fee=None,
        ttc=Decimal("6.25"),
        type_detail=SessionTransactionTypeDetail.EXISTING_STOCK,
    )

    consumed = await service.create_consumed_material(
        user_id=user.id, item_id=item.id, quantity=4
    )

    transaction = await test_db_session.scalar(
        select(SessionTransaction).where(SessionTransaction.session_id == consumed.id)
    )
    line = await test_db_session.scalar(
        select(SessionLine).where(SessionLine.session_id == consumed.id)
    )
    assert line is not None
    line_transaction = await test_db_session.scalar(
        select(SessionLineTransaction).where(SessionLineTransaction.session_line_id == line.id)
    )
    lot = await test_db_session.scalar(select(Lot).where(Lot.user_id == user.id))

    assert transaction is not None
    assert transaction.type is SessionTransactionType.CONSUMED
    assert transaction.status is SessionTransactionStatus.SOLDED
    assert line.qty == 4
    assert line_transaction is not None
    assert line_transaction.tt == Decimal("5.00000")
    assert line_transaction.ttc == Decimal("5.00000")
    assert line_transaction.fee == Decimal("0.00")
    assert lot is not None
    assert lot.qty == 1
    assert lot.reserved == 0
