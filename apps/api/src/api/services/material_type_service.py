"""Business operations for material type catalogue data."""

import logging

from api.db.models import MaterialType
from api.db.repositories import MaterialTypeRepository

logger = logging.getLogger(__name__)


class MaterialTypeService:
    """Provide material type catalogue use cases."""

    def __init__(self, repository: MaterialTypeRepository) -> None:
        """Store the repository used to load material types."""

        self._repository = repository

    async def get_all(self) -> list[MaterialType]:
        """Return active material types available to catalogue consumers."""

        logger.debug("material_type.get_all.start")
        types = await self._repository.get_all()
        logger.debug("material_type.get_all.success count=%d", len(types))
        return types
