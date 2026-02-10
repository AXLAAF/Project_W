"""
User repository for database operations.
"""
from typing import Optional, Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.models.user import User, Profile
from app.core.models.role import Role, UserRole


class UserRepository:
    """Repository for User database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID with profile and roles."""
        query = (
            select(User)
            .options(
                selectinload(User.profile),
                selectinload(User.user_roles).selectinload(UserRole.role),
            )
            .where(User.id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email with profile and roles."""
        query = (
            select(User)
            .options(
                selectinload(User.profile),
                selectinload(User.user_roles).selectinload(UserRole.role),
            )
            .where(User.email == email)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        is_active: Optional[bool] = None,
    ) -> tuple[Sequence[User], int]:
        """Get all users with pagination."""
        query = select(User).options(
            selectinload(User.profile),
            selectinload(User.user_roles).selectinload(UserRole.role),
        )
        count_query = select(func.count()).select_from(User)

        if is_active is not None:
            query = query.where(User.is_active == is_active)
            count_query = count_query.where(User.is_active == is_active)

        query = query.offset(offset).limit(limit).order_by(User.created_at.desc())

        result = await self.session.execute(query)
        count_result = await self.session.execute(count_query)

        return result.scalars().all(), count_result.scalar_one()

    async def create(
        self,
        email: str,
        password_hash: str,
        profile_data: dict,
    ) -> User:
        """Create a new user with profile."""
        user = User(
            email=email,
            password_hash=password_hash,
        )
        self.session.add(user)
        await self.session.flush()  # Get user ID

        profile = Profile(user_id=user.id, **profile_data)
        self.session.add(profile)
        user.profile = profile

        return user

    async def update(self, user: User, **kwargs) -> User:
        """Update user fields."""
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        await self.session.flush()
        return user

    async def delete(self, user: User) -> None:
        """Delete a user."""
        await self.session.delete(user)

    async def assign_role(self, user: User, role: Role, assigned_by: Optional[int] = None) -> None:
        """Assign a role to a user."""
        user_role = UserRole(user_id=user.id, role_id=role.id, assigned_by=assigned_by)
        self.session.add(user_role)

    async def remove_role(self, user: User, role: Role) -> None:
        """Remove a role from a user."""
        query = select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == role.id,
        )
        result = await self.session.execute(query)
        user_role = result.scalar_one_or_none()
        if user_role:
            await self.session.delete(user_role)

    async def get_role_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        query = select(Role).where(Role.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_or_create_role(self, name: str, description: str = "") -> Role:
        """Get existing role or create new one."""
        role = await self.get_role_by_name(name)
        if not role:
            role = Role(name=name, description=description)
            self.session.add(role)
            await self.session.flush()
        return role
