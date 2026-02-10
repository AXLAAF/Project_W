"""
Login User Use Case.
"""
from datetime import timedelta
from typing import Optional

from app.domain.repositories.user_repository import IUserRepository
from app.domain.services.password_service import IPasswordService
from app.domain.services.token_service import ITokenService
from app.application.dtos.user_dtos import LoginDTO, TokenResponseDTO


class LoginUserUseCase:
    """Use case to authenticate user and issue tokens."""
    
    def __init__(
        self,
        user_repo: IUserRepository,
        password_service: IPasswordService,
        token_service: ITokenService
    ):
        self._user_repo = user_repo
        self._password_service = password_service
        self._token_service = token_service
    
    async def execute(self, data: LoginDTO) -> TokenResponseDTO:
        user = await self._user_repo.get_by_email(data.email)
        
        if not user or not user.password_hash:
            raise ValueError("Invalid credentials")
            
        if not self._password_service.verify_password(data.password, user.password_hash):
            raise ValueError("Invalid credentials")
            
        if not user.is_active:
            raise ValueError("User account is inactive")
            
        # Create tokens
        # Assuming we put user_id and roles in token
        token_data = {
            "sub": str(user.id),
            "email": str(user.email),
            "roles": user.roles
        }
        
        access_token = self._token_service.create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=30) # Configurable
        )
        
        refresh_token = self._token_service.create_refresh_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(days=7)
        )
        
        return TokenResponseDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60
        )
