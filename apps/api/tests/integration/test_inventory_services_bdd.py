from datetime import datetime, timezone
from uuid import uuid4

import pytest

from api.core.exceptions import UnprocessingError
from api.db.models import (
    Item,
    Lot,
    LotType,
    Material,
    MaterialType,
    Session,
    SessionLine,
    SessionLineType,
    User,
)
from api.db.repositories import ItemRepository, SessionLineRepository
from api.services.item_service import ItemService
from api.services.lot_service import get_lot_service
from api.services.session_line_service import SessionLineService


async def _create_user(test_db_session, prefix: str) -> User:
    """Create a unique BDD user and flush it to obtain its database id."""

    user = User(pseudo=f"bdd-{prefix}-{uuid4().hex[:10]}", password_hash="hash")
    test_db_session.add(user)
    await test_db_session.flush()
    return user


async def _create_item(test_db_session, *, stackable: bool) -> Item:
    """Create a catalogue item with or without its material detail row."""

    item = Item(name=f"BDD item {uuid4()}")
    test_db_session.add(item)
    await test_db_session.flush()
    if stackable:
        material_type = MaterialType(name=f"BDD type {uuid4()}")
        test_db_session.add(material_type)
        await test_db_session.flush()
        test_db_session.add(Material(item_id=item.id, type=material_type.id))
        await test_db_session.flush()
    return item


async def _create_line(test_db_session, *, user: User, item: Item) -> SessionLine:
    """Create an owned produced line for an item."""

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
    return line


async def test_bdd_item_service_reads_stackability_from_catalogue(test_db_session):
    """Given catalogue details, item service returns true, false, or unknown."""

    stackable_item = await _create_item(test_db_session, stackable=True)
    non_stackable_item = await _create_item(test_db_session, stackable=False)
    service = ItemService(ItemRepository(test_db_session))

    assert await service.is_item_stackable(item_id=stackable_item.id) is True
    assert await service.is_item_stackable(item_id=non_stackable_item.id) is False
    assert await service.is_item_stackable(item_id=uuid4()) is None


async def test_bdd_session_line_service_enforces_parent_session_owner(
    test_db_session,
):
    """Given two users, session-line service only returns the owner's line."""

    owner = await _create_user(test_db_session, "owner")
    other_user = await _create_user(test_db_session, "other")
    item = await _create_item(test_db_session, stackable=True)
    line = await _create_line(test_db_session, user=owner, item=item)
    service = SessionLineService(SessionLineRepository(test_db_session))

    assert (
        await service.get_session_line_for_user(
            session_line_id=line.id,
            user_id=owner.id,
        )
    ).id == line.id
    assert (
        await service.get_session_line_for_user(
            session_line_id=line.id,
            user_id=other_user.id,
        )
        is None
    )


async def test_bdd_lot_service_returns_only_usable_owned_lots_in_fifo_order(
    test_db_session,
):
    """Given inventory lots, lot service returns only usable lots oldest first."""

    owner = await _create_user(test_db_session, "lots-owner")
    other_user = await _create_user(test_db_session, "lots-other")
    item = await _create_item(test_db_session, stackable=True)
    old_line = await _create_line(test_db_session, user=owner, item=item)
    new_line = await _create_line(test_db_session, user=owner, item=item)
    zero_line = await _create_line(test_db_session, user=owner, item=item)
    inactive_line = await _create_line(test_db_session, user=owner, item=item)
    other_line = await _create_line(test_db_session, user=other_user, item=item)
    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    lots = [
        Lot(
            user_id=owner.id,
            type=LotType.TRANSACTION,
            origin_id=str(old_line.id),
            qty=10,
            created_at=base_time,
            is_active=True,
        ),
        Lot(
            user_id=owner.id,
            type=LotType.TRANSACTION,
            origin_id=str(new_line.id),
            qty=5,
            created_at=base_time.replace(day=2),
            is_active=True,
        ),
        Lot(
            user_id=owner.id,
            type=LotType.TRANSACTION,
            origin_id=str(zero_line.id),
            qty=0,
            created_at=base_time.replace(day=3),
            is_active=True,
        ),
        Lot(
            user_id=owner.id,
            type=LotType.TRANSACTION,
            origin_id=str(inactive_line.id),
            qty=5,
            created_at=base_time.replace(day=4),
            is_active=False,
        ),
        Lot(
            user_id=other_user.id,
            type=LotType.TRANSACTION,
            origin_id=str(other_line.id),
            qty=5,
            created_at=base_time.replace(day=5),
            is_active=True,
        ),
    ]
    test_db_session.add_all(lots)
    await test_db_session.flush()

    result_item, result_lots, total_quantity = await get_lot_service(
        test_db_session
    ).get_fifo_lots(
        user_id=owner.id,
        item_id=item.id,
    )

    assert result_item.id == item.id
    origins = [lot.origin for lot in result_lots]
    assert all(origin is not None for origin in origins)
    assert [origin.id for origin in origins if origin is not None] == [
        old_line.id,
        new_line.id,
    ]
    assert total_quantity == 15
    first_origin = result_lots[0].origin
    assert first_origin is not None
    assert first_origin.session.user_id == owner.id
    assert first_origin.item is not None
    assert first_origin.item.id == item.id


async def test_bdd_lot_service_rejects_non_stackable_item(test_db_session):
    """Given a non-stackable item, lot service returns a conflict."""

    item = await _create_item(test_db_session, stackable=False)

    with pytest.raises(UnprocessingError) as error:
        await get_lot_service(test_db_session).get_fifo_lots(
            user_id=uuid4(), item_id=item.id
        )

    assert error.value.status_code == 409
