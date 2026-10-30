from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError

from api.core.exceptions import AppError
from api.db.models import (
    Item,
    Lot,
    LotKind,
    MaterialLot,
    Session,
    SessionLine,
    SessionLineType,
    ToolLot,
    User,
)
from api.services.lot_service import get_lot_service


async def given_user_with_produced_line(test_db_session):
    """Given a user owns a produced line referencing a catalogue item."""

    user = User(pseudo=f"bdd-{uuid4().hex[:12]}", password_hash="hash")
    item = Item(name=f"BDD item {uuid4()}")
    test_db_session.add_all([user, item])
    await test_db_session.flush()
    mining_session = Session(user_id=user.id)
    test_db_session.add(mining_session)
    await test_db_session.flush()
    line = SessionLine(
        session_id=mining_session.id,
        item_id=item.id,
        type=SessionLineType.PRODUCED,
    )
    test_db_session.add(line)
    await test_db_session.flush()
    await test_db_session.commit()
    return user, item, line


async def test_bdd_material_lot_creation_is_atomic_and_owned(test_db_session):
    """Given a produced line, when a material lot is created, then it is owned and specialized."""

    user, item, line = await given_user_with_produced_line(test_db_session)

    lot = await get_lot_service(test_db_session).create_lot(
        user_id=user.id,
        kind=LotKind.MATERIAL,
        session_line_id=line.id,
        quantity=25,
        tt=None,
    )

    stored_lot = await test_db_session.scalar(select(Lot).where(Lot.id == lot.id))
    specialized_lot = await test_db_session.scalar(
        select(MaterialLot).where(MaterialLot.lot_id == lot.id)
    )
    refreshed_line = await test_db_session.scalar(
        select(SessionLine).where(SessionLine.id == line.id)
    )

    assert stored_lot is not None
    assert stored_lot.user_id == user.id
    assert stored_lot.origin_id == str(line.id)
    assert stored_lot.qty == 25
    assert stored_lot.reserved == 0
    assert specialized_lot is not None
    assert refreshed_line.lot_id is None
    assert item.id == line.item_id


async def test_bdd_tool_lot_persists_tt(test_db_session):
    """Given a produced line, when a tool lot is created, then its TT is stored."""

    user, _item, line = await given_user_with_produced_line(test_db_session)

    lot = await get_lot_service(test_db_session).create_lot(
        user_id=user.id,
        kind=LotKind.TOOL,
        session_line_id=line.id,
        quantity=1,
        tt=Decimal("12.34500"),
    )

    tool_lot = await test_db_session.scalar(
        select(ToolLot).where(ToolLot.lot_id == lot.id)
    )

    assert tool_lot is not None
    assert str(tool_lot.tt) == "12.34500"


async def test_bdd_other_user_cannot_create_from_the_line(test_db_session):
    """Given another user's produced line, when creation is attempted, then it fails."""

    owner, _item, line = await given_user_with_produced_line(test_db_session)
    owner_id = owner.id
    other_user = User(pseudo=f"bdd-other-{uuid4().hex[:10]}", password_hash="hash")
    test_db_session.add(other_user)
    await test_db_session.flush()
    other_user_id = other_user.id
    await test_db_session.commit()

    with pytest.raises(AppError) as error:
        await get_lot_service(test_db_session).create_lot(
            user_id=other_user_id,
            kind=LotKind.MATERIAL,
            session_line_id=line.id,
            quantity=1,
            tt=None,
        )

    assert error.value.status_code == 404
    assert owner_id != other_user_id


async def test_bdd_trigger_enforces_produced_and_consumed_rules(test_db_session):
    """Given session lines, then the database trigger enforces item/lot ownership rules."""

    user = User(pseudo=f"bdd-trigger-{uuid4().hex[:10]}", password_hash="hash")
    item = Item(name=f"BDD trigger item {uuid4()}")
    test_db_session.add_all([user, item])
    await test_db_session.flush()
    mining_session = Session(user_id=user.id)
    test_db_session.add(mining_session)
    await test_db_session.flush()
    await test_db_session.commit()

    with pytest.raises(DBAPIError, match="requires item_id"):
        async with test_db_session.begin_nested():
            await test_db_session.execute(
                text(
                    """
                    INSERT INTO session_line (id, session_id, item_id, type)
                    VALUES (gen_random_uuid(), :session_id, NULL, 'PRODUCED')
                    """
                ),
                {"session_id": mining_session.id},
            )

    with pytest.raises(DBAPIError, match="cannot have item_id"):
        async with test_db_session.begin_nested():
            await test_db_session.execute(
                text(
                    """
                    INSERT INTO session_line (id, session_id, item_id, type)
                    VALUES (gen_random_uuid(), :session_id, :item_id, 'CONSUMED')
                    """
                ),
                {"session_id": mining_session.id, "item_id": item.id},
            )
