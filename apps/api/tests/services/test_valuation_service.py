from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from api.db.repositories import ItemRepository
from api.db.repositories.valuation_repository import ValuationRepository
from api.schemas.valuation_schema import (
    ItemLotsValuationResponse,
    ValuationSessionType,
)
from api.services.valuation_service import ValuationService


async def test_lot_valuation_propagates_absolute_contribution_through_refinage():
    """Keep the source TT contribution constant across a refining chain."""

    user_id = uuid4()
    item_id = uuid4()
    origin_lot_id = uuid4()
    refined_lot_id = uuid4()
    origin_session_id = uuid4()
    refinage_session_id = uuid4()
    sale_session_id = uuid4()
    repository = MagicMock(spec=ValuationRepository)
    repository.get_lot_graph = AsyncMock(
        return_value=(
                [
                    {
                        "lot_id": origin_lot_id,
                        "line_id": uuid4(),
                        "item_id": item_id,
                        "origin_quantity": 100,
                        "session_id": origin_session_id,
                        "transaction_type": "BUY",
                        "tt": Decimal(100),
                        "ttc": Decimal(120),
                        "economy_tt": Decimal(1),
                        "mining_session_id": None,
                        "refinage_session_id": None,
                    },
                    {
                        "lot_id": refined_lot_id,
                        "line_id": uuid4(),
                        "item_id": item_id,
                        "origin_quantity": 200,
                        "session_id": refinage_session_id,
                        "transaction_type": None,
                        "tt": None,
                        "ttc": None,
                        "economy_tt": Decimal(1),
                        "mining_session_id": None,
                        "refinage_session_id": refinage_session_id,
                    },
                ],
                [
                    {
                        "lot_id": origin_lot_id,
                        "session_id": refinage_session_id,
                        "tt": Decimal(50),
                        "ttc": None,
                        "fee": None,
                        "transaction_type": None,
                        "transaction_status": None,
                        "refinage_session_id": refinage_session_id,
                    },
                    {
                        "lot_id": refined_lot_id,
                        "session_id": sale_session_id,
                        "tt": Decimal(100),
                        "ttc": Decimal(140),
                        "fee": Decimal(5),
                        "transaction_type": "SELL",
                        "transaction_status": "SOLDED",
                        "refinage_session_id": None,
                    },
                ],
        )
    )
    item_repository = MagicMock(spec=ItemRepository)
    item_repository.get_item_with_economy = AsyncMock(return_value=object())

    valuation = await ValuationService(repository, item_repository).get_item_lot_valuation(
        user_id=user_id,
        item_id=item_id,
        session_type=ValuationSessionType.TRANSACTION,
    )

    assert valuation is not None
    response = ItemLotsValuationResponse.model_validate(valuation)
    assert response.lots[0].generated_sell_profit == Decimal("8.75")
    assert response.lots[0].origin_session_id == origin_session_id
