"""
Register User Use Case.
"""
from typing import Optional

from app.domain.repositories.user_repository import IUserRepository
from app.domain.repositories.role_repository import IRoleRepository
from app.domain.services.password_service import IPasswordService
from app.domain.entities.user import User, Profile
from app.domain.value_objects.email import Email
from app.application.dtos.user_dtos import RegisterUserDTO, UserProfileDTO, ProfileDTO


class RegisterUserUseCase:
    """Use case to register a new user."""
    
    def __init__(
        self,
        user_repo: IUserRepository,
        role_repo: IRoleRepository,
        password_service: IPasswordService
    ):
        self._user_repo = user_repo
        self._role_repo = role_repo
        self._password_service = password_service
    
    async def execute(self, data: RegisterUserDTO) -> UserProfileDTO:
        # Check if email exists
        existing = await self._user_repo.get_by_email(data.email)
        if existing:
            raise ValueError("Email already registered")
            
        # Hash password
        hashed_password = self._password_service.hash_password(data.password)
        
        # Create entities
        profile = Profile(
            first_name=data.profile.first_name,
            last_name=data.profile.last_name,
            student_id=data.profile.student_id,
            employee_id=data.profile.employee_id,
            department=data.profile.department,
            program=data.profile.program,
            phone=data.profile.phone,
        )
        
        user = User(
            email=Email(data.email),
            password_hash=hashed_password,
            profile=profile,
            is_active=True,
            is_verified=False
        )
        
        # Save user
        saved_user = await self._user_repo.save(user)
        
        # Assign default role based on context (Student vs Professor)
        default_role_name = "ALUMNO" if profile.student_id else "PROFESOR" 
        
        # Get or create role and assign
        role = await self._role_repo.get_or_create(default_role_name)
        if role and saved_user.id:
            await self._role_repo.assign_to_user(saved_user.id, role)
            # Update local user object roles for return
            saved_user.roles.append(role.name)
        
        return self._to_dto(saved_user)

    def _to_dto(self, user: User) -> UserProfileDTO:
        profile_dto = None
        if user.profile:
            profile_dto = ProfileDTO(
                id=user.profile.id if user.profile.id else 0,
                user_id=user.id if user.id else 0,
                first_name=user.profile.first_name,
                last_name=user.profile.last_name,
                full_name=user.profile.full_name,
                student_id=user.profile.student_id,
                employee_id=user.profile.employee_id,
                department=user.profile.department,
                program=user.profile.program,
                photo_url=user.profile.photo_url,
                phone=user.profile.phone,
            )
            
        return UserProfileDTO(
            id=user.id if user.id else 0,
            email=str(user.email),
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            profile=profile_dto,
            roles=user.roles
        )
