"""
Use case: Deactivate user.
"""
from app.domain.repositories.user_repository import IUserRepository
from app.domain.exceptions import UserNotFoundError


class DeactivateUserUseCase:
    """
    Deactivate a user account (admin only).
    
    Soft-deletes a user by setting is_active=False.
    """
    
    def __init__(self, user_repository: IUserRepository):
        self._user_repo = user_repository
    
    async def execute(self, user_id: int, deactivated_by: int) -> None:
        """
        Execute the use case.
        
        Args:
            user_id: ID of user to deactivate
            deactivated_by: ID of admin performing the action
        
        Raises:
            UserNotFoundError: If user is not found
        """
        user = await self._user_repo.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundError(user_id)
        
        user.deactivate()
        await self._user_repo.update(user)
