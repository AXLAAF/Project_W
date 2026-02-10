"""
Auth API Router (Hexagonal Architecture).
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.interfaces.dependencies import (
    get_login_use_case,
    get_register_use_case,
    get_refresh_token_use_case,
    get_current_active_user,
    get_token_service,
)
from app.application.use_cases.login_user import LoginUserUseCase
from app.application.use_cases.register_user import RegisterUserUseCase
from app.application.use_cases.refresh_token import RefreshTokenUseCase
from app.domain.entities.user import User
from app.domain.services.token_service import ITokenService

# Schemas (Input adapters)
from app.core.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse
from app.core.schemas.user import UserCreate, UserRead
from app.application.dtos.user_dtos import LoginDTO, RegisterUserDTO, ProfileCreateDTO

router = APIRouter()

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    user_data: UserCreate,
    use_case: Annotated[RegisterUserUseCase, Depends(get_register_use_case)],
) -> UserRead:
    """Register a new user."""
    # Adapter: Pydantic -> DTO
    register_dto = RegisterUserDTO(
        email=user_data.email,
        password=user_data.password,
        profile=ProfileCreateDTO(
            first_name=user_data.profile.first_name,
            last_name=user_data.profile.last_name,
            student_id=user_data.profile.student_id,
            employee_id=user_data.profile.employee_id,
            department=user_data.profile.department,
            program=user_data.profile.program,
            phone=user_data.profile.phone,
        )
    )
    
    try:
        result = await use_case.execute(register_dto)
        # Adapter: DTO -> Pydantic response (implicit via response_model)
        # We need to map DTO fields to Schema fields if they differ significantly
        # UserRead expects 'profile' as ProfileRead schema
        return result # The DTO structure should match enough or be compatible
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    use_case: Annotated[LoginUserUseCase, Depends(get_login_use_case)],
) -> TokenResponse:
    """Login and get tokens."""
    dto = LoginDTO(email=login_data.email, password=login_data.password)
    try:
        result = await use_case.execute(dto)
        return TokenResponse(
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            expires_in=result.expires_in
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: RefreshTokenRequest,
    use_case: Annotated[RefreshTokenUseCase, Depends(get_refresh_token_use_case)],
) -> TokenResponse:
    """Refresh access token."""
    try:
        result = await use_case.execute(token_data.refresh_token)
        return TokenResponse(
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            expires_in=result.expires_in
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> None:
    """Logout (stateless)."""
    pass
