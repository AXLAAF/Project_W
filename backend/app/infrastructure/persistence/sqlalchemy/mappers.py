"""
Mappers for converting between domain entities and SQLAlchemy models.
"""
from datetime import datetime
from typing import List, Optional

from app.domain.entities.user import User
from app.domain.entities.profile import Profile
from app.domain.entities.role import Role, UserRole
from app.domain.value_objects.email import Email

# Import ORM models from existing location
from app.core.models.user import User as UserModel, Profile as ProfileModel
from app.core.models.role import Role as RoleModel, UserRole as UserRoleModel


class RoleMapper:
    """Mapper for Role entity <-> RoleModel."""
    
    @staticmethod
    def to_entity(model: RoleModel) -> Role:
        """Convert ORM model to domain entity."""
        return Role(
            id=model.id,
            name=model.name,
            description=model.description or "",
            created_at=model.created_at,
        )
    
    @staticmethod
    def to_model(entity: Role) -> RoleModel:
        """Convert domain entity to ORM model."""
        model = RoleModel(
            name=entity.name,
            description=entity.description,
        )
        if entity.id:
            model.id = entity.id
        return model


class UserRoleMapper:
    """Mapper for UserRole entity <-> UserRoleModel."""
    
    @staticmethod
    def to_entity(model: UserRoleModel) -> UserRole:
        """Convert ORM model to domain entity."""
        return UserRole(
            id=model.id,
            user_id=model.user_id,
            role=RoleMapper.to_entity(model.role),
            assigned_at=model.assigned_at,
            assigned_by=model.assigned_by,
        )


class ProfileMapper:
    """Mapper for Profile entity <-> ProfileModel."""
    
    @staticmethod
    def to_entity(model: ProfileModel) -> Profile:
        """Convert ORM model to domain entity."""
        return Profile(
            id=model.id,
            user_id=model.user_id,
            first_name=model.first_name,
            last_name=model.last_name,
            student_id=model.student_id,
            employee_id=model.employee_id,
            department=model.department,
            program=model.program,
            photo_url=model.photo_url,
            phone=model.phone,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    @staticmethod
    def to_model(entity: Profile, user_id: int) -> ProfileModel:
        """Convert domain entity to ORM model."""
        model = ProfileModel(
            user_id=user_id,
            first_name=entity.first_name,
            last_name=entity.last_name,
            student_id=entity.student_id,
            employee_id=entity.employee_id,
            department=entity.department,
            program=entity.program,
            photo_url=entity.photo_url,
            phone=entity.phone,
        )
        if entity.id:
            model.id = entity.id
        return model


class UserMapper:
    """Mapper for User entity <-> UserModel."""
    
    @staticmethod
    def to_entity(model: UserModel) -> User:
        """Convert ORM model to domain entity."""
        profile = None
        if model.profile:
            profile = ProfileMapper.to_entity(model.profile)
        
        roles: List[UserRole] = []
        if model.user_roles:
            roles = [UserRoleMapper.to_entity(ur) for ur in model.user_roles]
        
        return User(
            id=model.id,
            email=Email(model.email),
            password_hash=model.password_hash,
            is_active=model.is_active,
            is_verified=model.is_verified,
            profile=profile,
            roles=roles,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    @staticmethod
    def to_model(entity: User) -> UserModel:
        """Convert domain entity to ORM model (without profile/roles)."""
        model = UserModel(
            email=entity.email_str,
            password_hash=entity.password_hash,
            is_active=entity.is_active,
            is_verified=entity.is_verified,
        )
        if entity.id:
            model.id = entity.id
        return model
    
    @staticmethod
    def update_model(model: UserModel, entity: User) -> None:
        """Update ORM model from domain entity."""
        model.email = entity.email_str
        model.is_active = entity.is_active
        model.is_verified = entity.is_verified
        
        if entity.profile and model.profile:
            model.profile.first_name = entity.profile.first_name
            model.profile.last_name = entity.profile.last_name
            model.profile.department = entity.profile.department
            model.profile.program = entity.profile.program
            model.profile.phone = entity.profile.phone
            model.profile.photo_url = entity.profile.photo_url
