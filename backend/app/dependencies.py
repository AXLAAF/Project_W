"""
FastAPI dependencies for authentication and authorization.
"""
from typing import Annotated, List

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User
from app.core.services.auth_service import AuthService, AuthenticationError
from app.shared.database import get_db

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Get current authenticated user from JWT token."""
    auth_service = AuthService(db)
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        return user
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Ensure current user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


def require_roles(required_roles: List[str]):
    """Dependency factory to require specific roles."""
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        user_roles = [ur.role.name for ur in current_user.user_roles]
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return role_checker


# Pre-defined role dependencies
require_admin = require_roles(["ADMIN_SISTEMA"])
require_coordinator = require_roles(["ADMIN_SISTEMA", "COORDINADOR"])
require_professor = require_roles(["ADMIN_SISTEMA", "COORDINADOR", "PROFESOR"])
require_resource_admin = require_roles(["ADMIN_SISTEMA", "ADMIN_RECURSOS"])
require_internship_manager = require_roles(["ADMIN_SISTEMA", "GESTOR_PRACTICAS"])

# Alias for backward compatibility
require_role = require_roles


def get_client_ip(request: Request) -> str:
    """Extract client IP from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """Extract User-Agent from request."""
    return request.headers.get("User-Agent", "unknown")
