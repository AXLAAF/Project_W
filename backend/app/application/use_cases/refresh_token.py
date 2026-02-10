"""
Use case: Refresh access token.
"""
from app.domain.repositories.user_repository import IUserRepository
from app.domain.services.token_service import ITokenService
from app.domain.exceptions import InvalidTokenError, InactiveUserError
from app.application.dtos.user_dtos import TokenResponseDTO


class RefreshTokenUseCase:
    """
    Refresh access token use case.
    
    Generates a new access token using a valid refresh token.
    """
    
    def __init__(
        self,
        user_repository: IUserRepository,
        token_service: ITokenService,
    ):
        self._user_repo = user_repository
        self._token_service = token_service
    
    async def execute(self, refresh_token: str) -> TokenResponseDTO:
        """
        Execute the use case.
        
        Args:
            refresh_token: The refresh token
        
        Returns:
            TokenResponseDTO with new access token
        
        Raises:
            InvalidTokenError: If token is invalid or expired
            InactiveUserError: If user is not active
        """
        # Decode and validate refresh token
        payload = self._token_service.decode_token(refresh_token)
        
        if not payload or not self._token_service.verify_token_type(payload, "refresh"):
            raise InvalidTokenError("Invalid refresh token")
        
        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenError("Invalid token payload")
        
        # Get user
        user = await self._user_repo.get_by_id(int(user_id))
        
        if not user:
            raise InvalidTokenError("User not found")
        
        if not user.is_active:
            raise InactiveUserError(user.id)
        
        # Create new access token
        token_data = {"sub": str(user.id), "email": user.email_str}
        access_token = self._token_service.create_access_token(token_data)
        
        return TokenResponseDTO(
            access_token=access_token,
            refresh_token=refresh_token,  # Keep same refresh token
            token_type="bearer",
            expires_in=self._token_service.access_token_expire_seconds,
        )
