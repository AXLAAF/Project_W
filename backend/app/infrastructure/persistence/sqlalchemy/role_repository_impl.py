"""
SQLAlchemy implementation of Role Repository.
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.role_repository import IRoleRepository
from app.domain.entities.role import Role
from app.core.models.role import Role as RoleModel


class SQLAlchemyRoleRepository(IRoleRepository):
    """SQLAlchemy implementation of role repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(self, name: str) -> Optional[Role]:
        stmt = select(RoleModel).where(RoleModel.name == name)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_id(self, role_id: int) -> Optional[Role]:
        stmt = select(RoleModel).where(RoleModel.id == role_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_roles(self) -> List[Role]:
        stmt = select(RoleModel)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_or_create(self, role_name: str, description: Optional[str] = None) -> Role:
        role = await self.get_by_name(role_name)
        if role:
            return role
            
        model = RoleModel(name=role_name, description=description)
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def assign_to_user(self, user_id: int, role: Role, assigned_by: Optional[int] = None) -> None:
        # Check if already assigned
        from app.core.models.role import UserRole
        
        stmt = select(UserRole).where(
            UserRole.user_id == user_id, 
            UserRole.role_id == role.id
        )
        result = await self.session.execute(stmt)
        if result.scalar_one_or_none():
            return
            
        user_role = UserRole(
            user_id=user_id,
            role_id=role.id,
            assigned_by=assigned_by
        )
        self.session.add(user_role)
        await self.session.commit()

    def _to_entity(self, model: RoleModel) -> Role:
        return Role(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at
        )
