"""
Use case: Assign role to user.
"""
from app.domain.repositories.user_repository import IUserRepository
from app.domain.repositories.role_repository import IRoleRepository
from app.domain.exceptions import UserNotFoundError
from app.application.dtos.user_dtos import UserProfileDTO, ProfileDTO


class AssignRoleUseCase:
    """
    Assign a role to a user (admin only).
    """
    
    def __init__(
        self,
        user_repository: IUserRepository,
        role_repository: IRoleRepository,
    ):
        self._user_repo = user_repository
        self._role_repo = role_repository
    
    async def execute(
        self,
        user_id: int,
        role_name: str,
        assigned_by: int,
    ) -> UserProfileDTO:
        """
        Execute the use case.
        
        Args:
            user_id: ID of user to assign role to
            role_name: Name of role to assign
            assigned_by: ID of admin performing the action
        
        Returns:
            Updated UserProfileDTO
        
        Raises:
            UserNotFoundError: If user is not found
        """
        user = await self._user_repo.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundError(user_id)
        
        # Get or create the role
        role = await self._role_repo.get_or_create(role_name.upper())
        
        # Assign role
        await self._role_repo.assign_to_user(user_id, role, assigned_by)
        
        # Refresh user to get updated roles
        user = await self._user_repo.get_by_id(user_id)
        
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
        
        return UserProfileDTO(
            id=user.id or 0,
            email=user.email_str,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            profile=profile_dto,
            roles=user.get_role_names(),
        )
