"""Business operations for mining claims."""

from contextlib import asynccontextmanager
from decimal import Decimal
from typing import TypedDict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AppError
from api.db.models import Claim, DepositSize
from api.db.repositories import ClaimRepository
from api.services.deposit_size_service import DepositSizeService
from api.services.session_line_service import (
    SessionLineService,
    get_session_line_service,
)


class ClaimCreateValues(TypedDict):
    """Validated values required to persist a newly created claim."""

    item_id: UUID
    qty: int
    is_hof: bool
    depth: Decimal | None
    latitude: int | None
    longitude: int | None
    is_depleted: bool


@asynccontextmanager
async def _transaction_scope(session: AsyncSession):
    """Open a transaction or savepoint for an atomic claim operation."""

    transaction = session.begin_nested() if session.in_transaction() else session.begin()
    async with transaction:
        yield


class ClaimService:
    """Provide owned claim CRUD and calculated claim enrichment."""

    def __init__(
        self,
        repository: ClaimRepository,
        deposit_size_service: DepositSizeService,
        session_line_service: SessionLineService,
    ) -> None:
        """Initialize claim persistence and the deposit-size catalogue service."""

        self._repository = repository
        self._deposit_size_service = deposit_size_service
        self._session_line_service = session_line_service

    async def get_all(
        self, *, session_id: UUID, user_id: UUID
    ) -> tuple[list[Claim], list[dict[str, object]]]:
        """Return enriched claims and quantity totals grouped by item identifier."""

        claims = await self._repository.get_all_for_user(
            session_id=session_id, user_id=user_id
        )
        deposit_sizes = await self._deposit_size_service.get_all()
        for claim in claims:
            self.enrich(claim=claim, deposit_sizes=deposit_sizes)
        totals: dict[UUID, int] = {}
        for claim in claims:
            totals[claim.item_id] = totals.get(claim.item_id, 0) + claim.qty
        result = [
            {"item_id": item_id, "qty": qty}
            for item_id, qty in totals.items()
        ]
        return claims, result

    async def create(
        self,
        *,
        session_id: UUID,
        user_id: UUID,
        values: ClaimCreateValues,
    ) -> Claim:
        """Create a claim for an owned session and return its enriched entity."""

        async with _transaction_scope(self._repository.session):
            is_depleted = values["is_depleted"]
            claim = await self._repository.create(
                session_id=session_id,
                item_id=values["item_id"],
                qty=values["qty"],
                is_hof=values["is_hof"],
                depth=values["depth"],
                latitude=values["latitude"],
                longitude=values["longitude"],
                depleted=is_depleted,
            )
            if is_depleted:
                await self._session_line_service.increment_produced_line_for_item(
                    session_id=session_id,
                    item_id=claim.item_id,
                    quantity=claim.qty,
                    user_id=user_id,
                )
            claim = await self._repository.get_for_user(
                claim_id=claim.id, session_id=session_id, user_id=user_id
            )
            if claim is None:
                raise AppError(404, "Mining session not found")
            self.enrich(
                claim=claim,
                deposit_sizes=await self._deposit_size_service.get_all(),
            )
            return claim

    async def update(
        self,
        *,
        claim_id: UUID,
        session_id: UUID,
        user_id: UUID,
        values: dict[str, object],
    ) -> Claim:
        """Update an owned claim and return its recalculated representation."""

        async with _transaction_scope(self._repository.session):
            claim = await self._repository.get_for_user(
                claim_id=claim_id, session_id=session_id, user_id=user_id
            )
            if claim is None:
                raise AppError(404, "Claim not found")
            values = {key: value for key, value in values.items() if value is not None}
            is_depleted = values.pop("is_depleted", None)
            if is_depleted is not None:
                values["depleted"] = is_depleted
            await self._repository.update(claim=claim, values=values)
            if is_depleted is True:
                await self._session_line_service.increment_produced_line_for_item(
                    session_id=session_id,
                    item_id=claim.item_id,
                    quantity=claim.qty,
                    user_id=user_id,
                )
            refreshed_claim = await self._repository.get_for_user(
                claim_id=claim_id, session_id=session_id, user_id=user_id
            )
            if refreshed_claim is None:
                raise AppError(404, "Claim not found")
            claim = refreshed_claim
            self.enrich(
                claim=claim,
                deposit_sizes=await self._deposit_size_service.get_all(),
            )
            return claim

    @staticmethod
    def enrich(*, claim: Claim, deposit_sizes: list[DepositSize]) -> None:
        """Attach calculated value and matching deposit size for response serialization."""

        economy = claim.item.economy if claim.item is not None else None
        value = (
            economy.tt * claim.qty
            if economy is not None and economy.tt is not None and claim.qty is not None
            else None
        )
        claim.calculated_value = value  # type: ignore[attr-defined]
        claim.calculated_deposit_size = (  # type: ignore[attr-defined]
            next(
                (
                    deposit_size
                    for deposit_size in deposit_sizes
                    if deposit_size.min <= value <= deposit_size.max
                ),
                None,
            )
            if value is not None
            else None
        )


def get_claim_service(session: AsyncSession) -> ClaimService:
    """Build a claim service for the current database session."""

    from api.db.repositories import DepositSizeRepository

    return ClaimService(
        ClaimRepository(session),
        DepositSizeService(DepositSizeRepository(session)),
        get_session_line_service(session),
    )
