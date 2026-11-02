"""Routes belonging to the mining domain."""

from fastapi import APIRouter

from .deposit_size_controller import router as deposit_size_router
from .mining_session_controller import router as mining_session_router

mining_router = APIRouter()
mining_router.include_router(deposit_size_router)
mining_router.include_router(mining_session_router)
