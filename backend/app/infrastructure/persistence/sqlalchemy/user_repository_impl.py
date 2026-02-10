"""
SQLAlchemy implementation of User Repository.
"""
from typing import List, Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.repositories.user_repository import IUserRepository
from app.domain.entities.user import User, Profile
from app.domain.value_objects.email import Email
from app.core.models.user import User as UserModel, Profile as ProfileModel
from app.core.models.role import UserRole  # Assuming this exists for role mapping


class SQLAlchemyUserRepository(IUserRepository):
    """SQLAlchemy implementation of user repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> Optional[User]:
        stmt = (
            select(UserModel)
            .options(
                selectinload(UserModel.profile),
                selectinload(UserModel.user_roles).selectinload(UserRole.role)
            )
            .where(UserModel.id == user_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = (
            select(UserModel)
            .options(
                selectinload(UserModel.profile),
                selectinload(UserModel.user_roles).selectinload(UserRole.role)
            )
            .where(UserModel.email == email)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, user: User) -> User:
        # Check if update or create
        if user.id:
            return await self._update(user)
        return await self._create(user)

    async def _create(self, user: User) -> User:
        model = UserModel(
            email=str(user.email),
            password_hash=user.password_hash,
            is_active=user.is_active,
            is_verified=user.is_verified,
            # Roles handling would be more complex here, usually Separate assignment
        )
        
        if user.profile:
            model.profile = ProfileModel(
                first_name=user.profile.first_name,
                last_name=user.profile.last_name,
                student_id=user.profile.student_id,
                employee_id=user.profile.employee_id,
                department=user.profile.department,
                program=user.profile.program,
                photo_url=user.profile.photo_url,
                phone=user.profile.phone,
            )
            
        self.session.add(model)
        await self.session.flush() # To get ID
        
        return self._to_entity(model)

    async def _update(self, user: User) -> User:
        stmt = select(UserModel).options(selectinload(UserModel.profile)).where(UserModel.id == user.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError(f"User with ID {user.id} not found")
            
        model.email = str(user.email)
        model.is_active = user.is_active
        model.is_verified = user.is_verified
        if user.password_hash:
             model.password_hash = user.password_hash
             
        if user.profile:
            if not model.profile:
                model.profile = ProfileModel(user_id=model.id)
            
            p = model.profile
            p.first_name = user.profile.first_name
            p.last_name = user.profile.last_name
            p.student_id = user.profile.student_id
            p.employee_id = user.profile.employee_id
            p.department = user.profile.department
            p.program = user.profile.program
            p.photo_url = user.profile.photo_url
            p.phone = user.profile.phone

        await self.session.flush()
        return self._to_entity(model)

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        stmt = (
            select(UserModel)
            .options(
                selectinload(UserModel.profile),
                selectinload(UserModel.user_roles).selectinload(UserRole.role)
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def delete(self, user_id: int) -> bool:
        stmt = delete(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    def _to_entity(self, model: UserModel) -> User:
        profile = None
        if model.profile:
            profile = Profile(
                id=model.profile.id,
                user_id=model.id,
                first_name=model.profile.first_name,
                last_name=model.profile.last_name,
                student_id=model.profile.student_id,
                employee_id=model.profile.employee_id,
                department=model.profile.department,
                program=model.profile.program,
                photo_url=model.profile.photo_url,
                phone=model.profile.phone,
            )
            
        roles = []
        if model.user_roles:
            roles = [ur.role.name for ur in model.user_roles if ur.role]

        return User(
            id=model.id,
            email=Email(model.email),
            is_active=model.is_active,
            is_verified=model.is_verified,
            password_hash=model.password_hash,
            created_at=model.created_at,
            updated_at=model.updated_at,
            profile=profile,
            roles=roles
        )
