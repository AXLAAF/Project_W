"""
User management service.
"""
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User, Profile
from app.core.models.audit import AuditLog, AuditAction
from app.core.repositories.user_repository import UserRepository
from app.core.schemas.user import UserUpdate, ProfileUpdate


class UserNotFoundError(Exception):
    """Raised when user is not found."""
    pass


class UserService:
    """Service for user management operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def get_user(self, user_id: int) -> User:
        """Get user by ID."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        return user

    async def get_user_by_email(self, email: str) -> User:
        """Get user by email."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise UserNotFoundError(f"User with email {email} not found")
        return user

    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        is_active: Optional[bool] = None,
    ) -> tuple[Sequence[User], int]:
        """List users with pagination."""
        offset = (page - 1) * page_size
        return await self.user_repo.get_all(
            offset=offset,
            limit=page_size,
            is_active=is_active,
        )

    async def update_user(
        self,
        user_id: int,
        user_data: UserUpdate,
        updated_by: Optional[int] = None,
        ip_address: Optional[str] = None,
    ) -> User:
        """Update user (admin operation)."""
        user = await self.get_user(user_id)
        
        update_data = user_data.model_dump(exclude_unset=True)
        if update_data:
            user = await self.user_repo.update(user, **update_data)

            # Audit log
            audit = AuditLog.log(
                action=AuditAction.USER_UPDATE,
                user_id=updated_by,
                entity_type="User",
                entity_id=user_id,
                details=update_data,
                ip_address=ip_address,
            )
            self.session.add(audit)

        return user

    async def update_profile(
        self,
        user: User,
        profile_data: ProfileUpdate,
        ip_address: Optional[str] = None,
    ) -> User:
        """Update user's own profile."""
        if not user.profile:
            raise UserNotFoundError("User profile not found")

        update_data = profile_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(user.profile, key, value)

        # Audit log
        audit = AuditLog.log(
            action=AuditAction.PROFILE_UPDATE,
            user_id=user.id,
            entity_type="Profile",
            entity_id=user.profile.id,
            details=update_data,
            ip_address=ip_address,
        )
        self.session.add(audit)

        return user

    async def deactivate_user(
        self,
        user_id: int,
        deactivated_by: int,
        ip_address: Optional[str] = None,
    ) -> User:
        """Deactivate a user account."""
        user = await self.get_user(user_id)
        user = await self.user_repo.update(user, is_active=False)

        # Audit log
        audit = AuditLog.log(
            action=AuditAction.USER_DELETE,
            user_id=deactivated_by,
            entity_type="User",
            entity_id=user_id,
            details={"deactivated": True},
            ip_address=ip_address,
        )
        self.session.add(audit)

        return user

    async def assign_role_to_user(
        self,
        user_id: int,
        role_name: str,
        assigned_by: int,
        ip_address: Optional[str] = None,
    ) -> User:
        """Assign a role to a user."""
        user = await self.get_user(user_id)
        role = await self.user_repo.get_or_create_role(role_name)
        
        await self.user_repo.assign_role(user, role, assigned_by)

        # Audit log
        audit = AuditLog.log(
            action=AuditAction.ROLE_ASSIGN,
            user_id=assigned_by,
            entity_type="UserRole",
            entity_id=user_id,
            details={"role": role_name},
            ip_address=ip_address,
        )
        self.session.add(audit)

        # Refresh user to get updated roles
        return await self.get_user(user_id)

    async def remove_role_from_user(
        self,
        user_id: int,
        role_name: str,
        removed_by: int,
        ip_address: Optional[str] = None,
    ) -> User:
        """Remove a role from a user."""
        user = await self.get_user(user_id)
        role = await self.user_repo.get_role_by_name(role_name)
        
        if role:
            await self.user_repo.remove_role(user, role)

            # Audit log
            audit = AuditLog.log(
                action=AuditAction.ROLE_REVOKE,
                user_id=removed_by,
                entity_type="UserRole",
                entity_id=user_id,
                details={"role": role_name},
                ip_address=ip_address,
            )
            self.session.add(audit)

        return await self.get_user(user_id)

    def get_user_roles(self, user: User) -> list[str]:
        """Get list of role names for a user."""
        return [ur.role.name for ur in user.user_roles]
