from decimal import Decimal
from uuid import uuid4

from api.db.models import (
    Item,
    Lot,
    LotType,
    Session,
    SessionLine,
    SessionLineTransaction,
    SessionLineType,
    SessionMining,
    SessionMiningSearchType,
    SessionTransaction,
    SessionTransactionStatus,
    SessionTransactionType,
    User,
)
from api.schemas.valuation_schema import ValuationSessionType
from api.services.valuation_service import get_valuation_service


async def test_bdd_valuation_weights_buy_and_mining_lots_by_scope(test_db_session):
    """Calculate historical and remaining percentages from real owned lots."""

    user = User(pseudo=f"valuation-{uuid4().hex[:12]}", password_hash="hash")
    item = Item(name=f"Valuation item {uuid4()}")
    test_db_session.add_all([user, item])
    await test_db_session.flush()

    buy_session = Session(user=user)
    buy_session.transaction = SessionTransaction(
        type=SessionTransactionType.BUY,
        status=SessionTransactionStatus.SOLDED,
    )
    buy_line = SessionLine(
        session=buy_session,
        item=item,
        type=SessionLineType.PRODUCED,
        qty=10,
    )
    buy_line.transaction = SessionLineTransaction(
        tt=Decimal(100),
        ttc=Decimal(120),
    )

    inactive_buy_session = Session(user=user)
    inactive_buy_session.transaction = SessionTransaction(
        type=SessionTransactionType.BUY,
        status=SessionTransactionStatus.SOLDED,
    )
    inactive_buy_line = SessionLine(
        session=inactive_buy_session,
        item=item,
        type=SessionLineType.PRODUCED,
        qty=10,
    )
    inactive_buy_line.transaction = SessionLineTransaction(
        tt=Decimal(100),
        ttc=Decimal(110),
    )

    mining_session = Session(user=user)
    mining_session.mining = SessionMining(
        clic=1,
        search_type=SessionMiningSearchType.E,
    )
    mining_line = SessionLine(
        session=mining_session,
        item=item,
        type=SessionLineType.PRODUCED,
        qty=5,
    )
    test_db_session.add_all(
        [buy_session, inactive_buy_session, mining_session, buy_line, inactive_buy_line, mining_line]
    )
    await test_db_session.flush()

    test_db_session.add_all(
        [
            Lot(
                user_id=user.id,
                type=LotType.TRANSACTION,
                origin_id=str(buy_line.id),
                qty=10,
                reserved=4,
                is_active=True,
            ),
            Lot(
                user_id=user.id,
                type=LotType.TRANSACTION,
                origin_id=str(inactive_buy_line.id),
                qty=10,
                is_active=False,
            ),
            Lot(
                user_id=user.id,
                type=LotType.MINING,
                origin_id=str(mining_line.id),
                qty=5,
                reserved=1,
                is_active=True,
            ),
        ]
    )
    await test_db_session.flush()

    service = get_valuation_service(test_db_session)
    all_valuation = await service.get_item_valuation(
        user_id=user.id,
        item_id=item.id,
    )
    transaction_valuation = await service.get_item_valuation(
        user_id=user.id,
        item_id=item.id,
        session_type=ValuationSessionType.TRANSACTION,
    )
    mining_valuation = await service.get_item_valuation(
        user_id=user.id,
        item_id=item.id,
        session_type=ValuationSessionType.MINING,
    )

    assert all_valuation is not None
    assert all_valuation["average_purchase_percent"] == Decimal("112.000000")
    assert all_valuation["remaining_purchase_percent"] == Decimal("112.000000")
    assert transaction_valuation is not None
    assert transaction_valuation["average_purchase_percent"] == Decimal("115.000000")
    assert transaction_valuation["remaining_purchase_percent"] == Decimal("120.000000")
    assert mining_valuation is not None
    assert mining_valuation["average_purchase_percent"] == Decimal("100.000000")
    assert mining_valuation["remaining_purchase_percent"] == Decimal("100.000000")
