"""Planning routers package."""
from app.planning.routers.subjects import router as subjects_router
from app.planning.routers.groups import router as groups_router
from app.planning.routers.enrollments import router as enrollments_router

__all__ = [
    "subjects_router",
    "groups_router",
    "enrollments_router",
]
