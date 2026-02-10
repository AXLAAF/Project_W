"""
Get User Profile Use Case.
"""
from typing import Optional

from app.domain.repositories.user_repository import IUserRepository
from app.application.dtos.user_dtos import UserProfileDTO, ProfileDTO
from app.domain.entities.user import User


class GetUserProfileUseCase:
    """Use case to get user profile."""
    
    def __init__(self, user_repo: IUserRepository):
        self._user_repo = user_repo
    
    async def execute(self, user_id: int) -> UserProfileDTO:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        return self._to_dto(user)
    
    def _to_dto(self, user: User) -> UserProfileDTO:
        profile_dto = None
        if user.profile:
            profile_dto = ProfileDTO(
                id=user.profile.id,
                user_id=user.id,
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
            id=user.id,
            email=str(user.email),
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            profile=profile_dto,
            roles=user.roles
        )
