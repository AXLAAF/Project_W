"""
Use case: Update user profile.
"""
from typing import Optional

from app.domain.repositories.user_repository import IUserRepository
from app.domain.exceptions import UserNotFoundError
from app.application.dtos.user_dtos import UserProfileDTO, ProfileDTO, ProfileUpdateDTO


class UpdateProfileUseCase:
    """
    Update user's own profile use case.
    
    Allows a user to update their profile information.
    """
    
    def __init__(self, user_repository: IUserRepository):
        """
        Initialize use case with dependencies.
        
        Args:
            user_repository: Repository for user operations
        """
        self._user_repo = user_repository
    
    async def execute(
        self,
        user_id: int,
        profile_data: ProfileUpdateDTO,
    ) -> UserProfileDTO:
        """
        Execute the use case.
        
        Args:
            user_id: ID of the user to update
            profile_data: Profile data to update
        
        Returns:
            Updated UserProfileDTO
        
        Raises:
            UserNotFoundError: If user is not found
        """
        user = await self._user_repo.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundError(user_id)
        
        if not user.profile:
            raise UserNotFoundError(f"Profile not found for user {user_id}")
        
        # Update profile fields
        user.profile.update(
            first_name=profile_data.first_name,
            last_name=profile_data.last_name,
            department=profile_data.department,
            program=profile_data.program,
            phone=profile_data.phone,
            photo_url=profile_data.photo_url,
        )
        
        # Persist changes
        updated_user = await self._user_repo.update(user)
        
        profile_dto = ProfileDTO(
            id=updated_user.profile.id or 0,
            user_id=updated_user.profile.user_id or updated_user.id or 0,
            first_name=updated_user.profile.first_name,
            last_name=updated_user.profile.last_name,
            full_name=updated_user.profile.full_name,
            student_id=updated_user.profile.student_id,
            employee_id=updated_user.profile.employee_id,
            department=updated_user.profile.department,
            program=updated_user.profile.program,
            photo_url=updated_user.profile.photo_url,
            phone=updated_user.profile.phone,
            created_at=updated_user.profile.created_at,
            updated_at=updated_user.profile.updated_at,
        )
        
        return UserProfileDTO(
            id=updated_user.id or 0,
            email=updated_user.email_str,
            is_active=updated_user.is_active,
            is_verified=updated_user.is_verified,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
            profile=profile_dto,
            roles=updated_user.get_role_names(),
        )
