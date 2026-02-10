"""
Use case: List users with pagination.
"""
from typing import Optional
import math

from app.domain.repositories.user_repository import IUserRepository
from app.application.dtos.user_dtos import UserProfileDTO, ProfileDTO, UserListDTO


class ListUsersUseCase:
    """
    List all users use case.
    
    Retrieves a paginated list of users. Requires coordinator or admin permissions.
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
        page: int = 1,
        page_size: int = 20,
        is_active: Optional[bool] = None,
    ) -> UserListDTO:
        """
        Execute the use case.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            is_active: Optional filter by active status
        
        Returns:
            UserListDTO with paginated users
        """
        offset = (page - 1) * page_size
        
        users, total = await self._user_repo.list_all(
            offset=offset,
            limit=page_size,
            is_active=is_active,
        )
        
        user_dtos = []
        for user in users:
            profile_dto = None
            if user.profile:
                profile_dto = ProfileDTO(
                    id=user.profile.id or 0,
                    user_id=user.profile.user_id or user.id or 0,
                    first_name=user.profile.first_name,
                    last_name=user.profile.last_name,
                    full_name=user.profile.full_name,
                    student_id=user.profile.student_id,
                    employee_id=user.profile.employee_id,
                    department=user.profile.department,
                    program=user.profile.program,
                    photo_url=user.profile.photo_url,
                    phone=user.profile.phone,
                    created_at=user.profile.created_at,
                    updated_at=user.profile.updated_at,
                )
            
            user_dtos.append(UserProfileDTO(
                id=user.id or 0,
                email=user.email_str,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at,
                profile=profile_dto,
                roles=user.get_role_names(),
            ))
        
        total_pages = math.ceil(total / page_size) if page_size > 0 else 0
        
        return UserListDTO(
            items=user_dtos,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
