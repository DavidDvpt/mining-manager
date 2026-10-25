"""Aggregator for version 1 public routes."""

from fastapi import APIRouter

from .finder_controller import router as finder_router

api_v1_router = APIRouter()
api_v1_router.include_router(finder_router, prefix="/finders")
