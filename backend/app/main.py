"""
SIGAIA - Sistema de Gestión Académica Integral con IA
Main FastAPI Application
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.interfaces.api.v1 import auth, users, risk
from app.interfaces.api.v1.planning import subjects, groups, enrollments
from app.internships.routers import (
    companies_router,
    positions_router,
    applications_router,
    internships_router,
)
from app.reservations.routers import resources_router, reservations_router
from app.shared.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        description="Sistema de Gestión Académica Integral con IA para Universidad",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers - Core module
    app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
    app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["users"])

    # Include routers - Planning module
    app.include_router(subjects.router, prefix=f"{settings.API_V1_PREFIX}")
    app.include_router(groups.router, prefix=f"{settings.API_V1_PREFIX}")
    app.include_router(enrollments.router, prefix=f"{settings.API_V1_PREFIX}")

    # Include routers - Risk module (Refactored)
    app.include_router(risk.router, prefix=f"{settings.API_V1_PREFIX}")

    # Include routers - Internships module
    app.include_router(companies_router, prefix=f"{settings.API_V1_PREFIX}")
    app.include_router(positions_router, prefix=f"{settings.API_V1_PREFIX}")
    app.include_router(applications_router, prefix=f"{settings.API_V1_PREFIX}")
    app.include_router(internships_router, prefix=f"{settings.API_V1_PREFIX}")

    # Include routers - Reservations module
    app.include_router(resources_router, prefix=f"{settings.API_V1_PREFIX}")
    app.include_router(reservations_router, prefix=f"{settings.API_V1_PREFIX}")

    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:
        return {"status": "healthy", "service": settings.APP_NAME}

    return app


app = create_application()
