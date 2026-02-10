"""Reservations routers package."""
from .resources import router as resources_router
from .reservations import router as reservations_router

__all__ = [
    "resources_router",
    "reservations_router",
]
