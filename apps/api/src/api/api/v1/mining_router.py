"""Routes belonging to the mining domain."""

from fastapi import APIRouter

from .deposit_size_controller import router as deposit_size_router

mining_router = APIRouter(prefix="/mining")
mining_router.include_router(deposit_size_router)
