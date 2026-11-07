"""Business operations for current inventory valuation."""

from collections.abc import Mapping
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, cast
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.db.repositories import ItemRepository
from api.db.repositories.item_repository import ItemCatalogueType
from api.db.repositories.valuation_repository import ValuationRepository
from api.schemas.valuation_schema import ValuationSessionType


def _decimal_value(value: object | None) -> Decimal:
    """Normalize a nullable database numeric value for arithmetic."""

    if value is None:
        return Decimal(0)
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


class ValuationService:
    """Calculate purchase-cost percentages for owned inventory."""

    def __init__(
        self,
        repository: ValuationRepository,
        item_repository: ItemRepository,
    ) -> None:
        """Store repositories needed for valuation and item existence checks."""

        self._repository = repository
        self._item_repository = item_repository

    async def get_item_valuation(
        self,
        *,
        user_id: UUID,
        item_id: UUID,
        session_type: ValuationSessionType = ValuationSessionType.ALL,
    ) -> dict[str, UUID | Decimal | datetime | None] | None:
        """Return historical and remaining purchase percentages for one item."""

        item = await self._item_repository.get_item_with_economy(item_id=item_id)
        if item is None:
            return None
        historical, remaining = await self._repository.get_item_purchase_percentages(
            user_id=user_id,
            item_id=item_id,
            session_type=session_type.value,
        )
        return {
            "item_id": item_id,
            "average_purchase_percent": historical,
            "remaining_purchase_percent": remaining,
            "calculated_at": datetime.now(UTC),
        }

    async def get_item_lot_valuation(
        self,
        *,
        user_id: UUID,
        item_id: UUID,
        session_type: ValuationSessionType = ValuationSessionType.ALL,
        item_type: ItemCatalogueType | None = None,
    ) -> dict[str, object] | None:
        """Return realized profit attributed to each owned origin lot."""

        item = await self._item_repository.get_item_with_economy(item_id=item_id)
        if item is None:
            return None
        if item_type is not None and not await self._item_repository.is_item_of_type(
            item_id=item_id, item_type=item_type
        ):
            return None
        lot_rows, consumed_rows = await self._repository.get_lot_graph(
            user_id=user_id
        )
        lots: dict[UUID, dict[str, object]] = {}
        children_by_session: dict[UUID, list[UUID]] = {}
        for row in lot_rows:
            transaction_type = getattr(row["transaction_type"], "value", row["transaction_type"])
            mining_session_id = row["mining_session_id"]
            if transaction_type == "BUY":
                origin_type = "TRANSACTION"
                origin_tt = _decimal_value(row["tt"])
                origin_ttc = _decimal_value(row["ttc"]) or origin_tt
            elif mining_session_id is not None:
                origin_type = "MINING"
                origin_tt = _decimal_value(row["economy_tt"]) * _decimal_value(
                    row["origin_quantity"]
                )
                origin_ttc = origin_tt
            elif row["refinage_session_id"] is not None:
                origin_type = "REFINAGE"
                origin_tt = _decimal_value(row["economy_tt"]) * _decimal_value(
                    row["origin_quantity"]
                )
                origin_ttc = origin_tt
            else:
                continue
            lot_id = row["lot_id"]
            lots[lot_id] = {
                "lot_id": lot_id,
                "origin_line_id": row["line_id"],
                "item_id": row["item_id"],
                "origin_session_id": row["session_id"],
                "origin_session_type": origin_type,
                "origin_tt": origin_tt,
                "origin_ttc": origin_ttc,
                "generated_sell_profit": Decimal(0),
            }
            children_by_session.setdefault(row["session_id"], []).append(lot_id)

        consumed_by_lot: dict[UUID, list[Mapping[Any, Any]]] = {}
        for row in consumed_rows:
            consumed_by_lot.setdefault(row["lot_id"], []).append(row)

        def trace(lot_id: UUID, contribution: Decimal, visited: set[UUID]) -> Decimal:
            """Propagate one source contribution through descendants and sales."""

            if lot_id in visited or lot_id not in lots:
                return Decimal(0)
            visited = visited | {lot_id}
            lot = lots[lot_id]
            origin_tt = lot["origin_tt"]
            if not isinstance(origin_tt, Decimal) or origin_tt <= 0:
                return Decimal(0)
            profit = Decimal(0)
            for line in consumed_by_lot.get(lot_id, []):
                line_tt = _decimal_value(line["tt"])
                factor = contribution / origin_tt
                line_transaction_type = getattr(
                    line["transaction_type"], "value", line["transaction_type"]
                )
                line_transaction_status = getattr(
                    line["transaction_status"], "value", line["transaction_status"]
                )
                if line_transaction_type == "SELL" and line_transaction_status == "SOLDED":
                    line_profit = (
                        _decimal_value(line["ttc"])
                        - line_tt
                        - _decimal_value(line["fee"])
                    )
                    profit += line_profit * factor
                elif line["refinage_session_id"] is not None:
                    passed_contribution = contribution * line_tt / origin_tt
                    child_ids = children_by_session.get(line["session_id"], [])
                    child_total = sum(
                        (
                            cast(Decimal, lots[child_id]["origin_tt"])
                            for child_id in child_ids
                        ),
                        Decimal(0),
                    )
                    if child_total > 0:
                        for child_id in child_ids:
                            child_tt = cast(Decimal, lots[child_id]["origin_tt"])
                            profit += trace(
                                child_id,
                                passed_contribution * child_tt / child_total,
                                visited,
                            )
            return profit

        result_lots = []
        for lot in lots.values():
            if lot["item_id"] != item_id or lot["origin_session_type"] not in {
                "MINING",
                "TRANSACTION",
            }:
                continue
            if session_type is ValuationSessionType.MINING and lot["origin_session_type"] != "MINING":
                continue
            if session_type is ValuationSessionType.TRANSACTION and lot["origin_session_type"] != "TRANSACTION":
                continue
            lot["generated_sell_profit"] = trace(
                cast(UUID, lot["lot_id"]),
                cast(Decimal, lot["origin_tt"]),
                set(),
            )
            result_lots.append(lot)
        return {
            "item_id": item_id,
            "lots": result_lots,
            "calculated_at": datetime.now(UTC),
        }


def get_valuation_service(session: AsyncSession) -> ValuationService:
    """Build a valuation service for the current database session."""

    return ValuationService(
        repository=ValuationRepository(session),
        item_repository=ItemRepository(session),
    )
