"""Aggregator for service-to-service routes."""

from fastapi import APIRouter

internal_router = APIRouter(include_in_schema=False)
