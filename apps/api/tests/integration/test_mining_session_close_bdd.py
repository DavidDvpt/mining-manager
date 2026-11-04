from uuid import uuid4

from sqlalchemy import select

from api.db.models import (
    Item,
    Lot,
    MaterialLot,
    Session,
    SessionLine,
    SessionLineType,
    SessionMining,
    SessionMiningSearchType,
    User,
)
from api.services import get_session_mining_service


async def test_bdd_closing_mining_session_creates_produced_lot(test_db_session):
    """Close a mining session and persist its final produced quantity as a lot."""

    user = User(pseudo=f"bdd-close-{uuid4().hex[:10]}", password_hash="hash")
    item = Item(name=f"BDD close item {uuid4()}")
    mining_session = Session(user=user)
    mining_session.mining = SessionMining(
        clic=1,
        search_type=SessionMiningSearchType.E,
    )
    produced_line = SessionLine(
        session=mining_session,
        item=item,
        type=SessionLineType.PRODUCED,
        qty=3,
    )
    test_db_session.add_all([user, item, mining_session, produced_line])
    await test_db_session.flush()

    closed_session = await get_session_mining_service(test_db_session).close(
        user_id=user.id,
        session_id=mining_session.id,
        tool_decays={},
        amplifier_tts={},
        enhancer_quantities={},
        produced_quantities={produced_line.id: 7},
    )

    assert closed_session.ended_at is not None
    assert produced_line.qty == 7

    produced_lot = await test_db_session.scalar(
        select(Lot).where(Lot.origin_id == str(produced_line.id))
    )
    assert produced_lot is not None
    assert produced_lot.user_id == user.id
    assert produced_lot.qty == 7

    material_lot = await test_db_session.scalar(
        select(MaterialLot).where(MaterialLot.lot_id == produced_lot.id)
    )
    assert material_lot is not None
