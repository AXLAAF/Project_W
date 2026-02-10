"""
Internships module routers.
"""
from app.internships.routers.companies import router as companies_router
from app.internships.routers.positions import router as positions_router
from app.internships.routers.applications import router as applications_router
from app.internships.routers.internships import router as internships_router

__all__ = [
    "companies_router",
    "positions_router",
    "applications_router",
    "internships_router",
]
