"""Aggregator for version 1 public routes."""

from fastapi import APIRouter

from .auth_controller import router as auth_router
from .enhancer_controller import router as enhancer_router
from .excavator_controller import router as excavator_router
from .finder_amplifier_controller import router as finder_amplifier_router
from .finder_controller import router as finder_router
from .material_controller import router as material_router
from .mining_router import mining_router
from .profile_controller import router as profile_router
from .refiner_controller import router as refiner_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(profile_router, prefix="/profile")
api_v1_router.include_router(excavator_router, prefix="/excavators")
api_v1_router.include_router(finder_router, prefix="/finders")
api_v1_router.include_router(finder_amplifier_router, prefix="/finder-amplifiers")
api_v1_router.include_router(enhancer_router, prefix="/enhancers")
api_v1_router.include_router(material_router, prefix="/materials")
api_v1_router.include_router(mining_router)
api_v1_router.include_router(refiner_router, prefix="/refiners")
