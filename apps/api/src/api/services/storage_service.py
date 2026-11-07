"""Business operations for authenticated user storage."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.db.repositories import MaterialRepository

from .lot_service import LotService, get_lot_service
from .material_service import MaterialService


class StorageService:
    """Provide storage inventory use cases."""

    def __init__(
        self, lot_service: LotService, material_service: MaterialService
    ) -> None:
        """Store services used to identify materials and query their stock."""

        self._lot_service = lot_service
        self._material_service = material_service

    async def get_material_stock(self, *, user_id: UUID) -> dict[UUID, int]:
        """Return available quantities for catalogue items typed as materials.

        Material membership comes from MaterialService. Lot filtering,
        ownership, and aggregation remain generic responsibilities of LotService.
        """

        materials = await self._material_service.get_all()
        return await self._lot_service.get_available_quantities(
            user_id=user_id,
            item_ids={material.id for material in materials},
        )

    async def get_material_stock_for_item(
        self, *, user_id: UUID, material_id: UUID
    ) -> dict[UUID, int]:
        """Return one material's available stock in the compact API format."""

        material = await self._material_service.get_by_id(material_id)
        if material is None:
            return {}
        stock = await self._lot_service.get_available_quantities(
            user_id=user_id,
            item_ids={material.id},
        )
        return stock


def get_storage_service(session: AsyncSession) -> StorageService:
    """Build storage orchestration with the existing catalogue and lot services."""

    return StorageService(
        lot_service=get_lot_service(session),
        material_service=MaterialService(MaterialRepository(session)),
    )
