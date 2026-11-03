from uuid import uuid4

import pytest

from api.core.exceptions import AppError, UnprocessingError
from api.db.models import (
    Item,
    Lot,
    LotType,
    MiningLoot,
    MiningLootType,
    Session,
    SessionLineType,
    SessionMining,
    SessionMiningSearchType,
    User,
)
from api.services.session_line_service import get_session_line_service


async def _mining_context(test_db_session):
    """Create an owned open mining session and one allowed loot item."""

    user = User(pseudo=f"bdd-lines-{uuid4().hex[:10]}", password_hash="hash")
    item = Item(name=f"BDD loot item {uuid4()}")
    test_db_session.add_all([user, item])
    await test_db_session.flush()
    test_db_session.add(
        MiningLoot(type=MiningLootType.E, resource_id=item.id)
    )
    mining_session = Session(user_id=user.id)
    mining_session.mining = SessionMining(
        clic=1,
        search_type=SessionMiningSearchType.E,
    )
    test_db_session.add(mining_session)
    await test_db_session.flush()
    return user, item, mining_session


async def test_bdd_mining_produced_line_lifecycle(test_db_session):
    """Create, update, and delete a produced line in an open mining session."""

    user, item, mining_session = await _mining_context(test_db_session)
    service = get_session_line_service(test_db_session)

    line = await service.create_produced_line(
        session_id=mining_session.id,
        item_id=item.id,
        quantity=3,
        user_id=user.id,
    )
    assert line.type is SessionLineType.PRODUCED
    assert line.item_id == item.id
    assert line.lot_id is None
    assert line.qty == 3

    updated = await service.update_produced_line_quantity(
        session_id=mining_session.id,
        session_line_id=line.id,
        quantity=8,
        user_id=user.id,
    )
    assert updated.qty == 8

    await service.delete_produced_line(
        session_id=mining_session.id,
        session_line_id=line.id,
        user_id=user.id,
    )
    assert (
        await service.get_session_line_for_user(
            session_line_id=line.id, user_id=user.id
        )
        is None
    )


async def test_bdd_mining_produced_line_requires_mining_loot(test_db_session):
    """Reject a produced line when its item is absent from mining loot."""

    user, _item, mining_session = await _mining_context(test_db_session)
    with pytest.raises(AppError) as error:
        await get_session_line_service(test_db_session).create_produced_line(
            session_id=mining_session.id,
            item_id=uuid4(),
            quantity=1,
            user_id=user.id,
        )

    assert error.value.status_code == 404


async def test_bdd_mining_produced_line_with_lot_cannot_be_deleted(
    test_db_session,
):
    """Reject deletion after a lot references the produced line as origin."""

    user, item, mining_session = await _mining_context(test_db_session)
    service = get_session_line_service(test_db_session)
    line = await service.create_produced_line(
        session_id=mining_session.id,
        item_id=item.id,
        quantity=1,
        user_id=user.id,
    )
    test_db_session.add(
        Lot(
            user_id=user.id,
            type=LotType.TRANSACTION,
            origin_id=str(line.id),
            qty=1,
        )
    )
    await test_db_session.flush()

    with pytest.raises(UnprocessingError) as error:
        await service.delete_produced_line(
            session_id=mining_session.id,
            session_line_id=line.id,
            user_id=user.id,
        )

    assert error.value.status_code == 409
