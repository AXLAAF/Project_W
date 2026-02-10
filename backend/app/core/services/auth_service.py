"""
Authentication service for login, registration, and token management.
"""
from datetime import timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.models.user import User
from app.core.models.audit import AuditLog, AuditAction
from app.core.repositories.user_repository import UserRepository
from app.core.schemas.user import UserCreate, UserRead
from app.core.schemas.auth import TokenResponse
from app.shared.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
    verify_token_type,
)


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class RegistrationError(Exception):
    """Raised when registration fails."""
    pass


class AuthService:
    """Service for authentication operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def register(
        self,
        user_data: UserCreate,
        ip_address: Optional[str] = None,
    ) -> User:
        """Register a new user."""
        # Check if email already exists
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise RegistrationError("Email already registered")

        # Validate institutional email (optional - customize domain)
        # if not user_data.email.endswith("@universidad.edu"):
        #     raise RegistrationError("Must use institutional email")

        # Create user
        password_hash = get_password_hash(user_data.password)
        user = await self.user_repo.create(
            email=user_data.email,
            password_hash=password_hash,
            profile_data=user_data.profile.model_dump(),
        )

        # Assign default role (ALUMNO)
        default_role = await self.user_repo.get_or_create_role(
            "ALUMNO", "Estudiante de la universidad"
        )
        await self.user_repo.assign_role(user, default_role)

        # Audit log
        audit = AuditLog.log(
            action=AuditAction.USER_CREATE,
            user_id=user.id,
            entity_type="User",
            entity_id=user.id,
            details={"email": user.email},
            ip_address=ip_address,
        )
        self.session.add(audit)

        return user

    async def login(
        self,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        """Authenticate user and return tokens."""
        user = await self.user_repo.get_by_email(email)

        # Check if user exists and password is correct
        if not user or not verify_password(password, user.password_hash):
            # Log failed attempt
            audit = AuditLog.log(
                action=AuditAction.LOGIN_FAILED,
                details={"email": email},
                ip_address=ip_address,
                user_agent=user_agent,
            )
            self.session.add(audit)
            raise AuthenticationError("Invalid email or password")

        # Check if user is active
        if not user.is_active:
            raise AuthenticationError("Account is deactivated")

        # Create tokens
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        # Audit log
        audit = AuditLog.log(
            action=AuditAction.LOGIN,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.session.add(audit)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Generate new access token using refresh token."""
        payload = decode_token(refresh_token)
        if not payload or not verify_token_type(payload, "refresh"):
            raise AuthenticationError("Invalid refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token payload")

        user = await self.user_repo.get_by_id(int(user_id))
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")

        # Create new access token
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,  # Keep same refresh token
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def get_current_user(self, token: str) -> User:
        """Get current user from access token."""
        payload = decode_token(token)
        if not payload or not verify_token_type(payload, "access"):
            raise AuthenticationError("Invalid access token")

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token payload")

        user = await self.user_repo.get_by_id(int(user_id))
        if not user:
            raise AuthenticationError("User not found")
        if not user.is_active:
            raise AuthenticationError("User is deactivated")

        return user

    async def logout(
        self,
        user: User,
        ip_address: Optional[str] = None,
    ) -> None:
        """Log out user (just audit log for now, tokens are stateless)."""
        audit = AuditLog.log(
            action=AuditAction.LOGOUT,
            user_id=user.id,
            ip_address=ip_address,
        )
        self.session.add(audit)
