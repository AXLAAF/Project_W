"""
Authentication API router.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User
from app.core.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.core.schemas.user import UserCreate, UserRead
from app.core.services.auth_service import AuthService, AuthenticationError, RegistrationError
from app.core.services.user_service import UserService
from app.dependencies import get_client_ip, get_current_active_user, get_user_agent
from app.shared.database import get_db

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    """
    Register a new user account.
    
    - Creates user with hashed password
    - Creates associated profile
    - Assigns default ALUMNO role
    """
    auth_service = AuthService(db)
    user_service = UserService(db)
    
    try:
        user = await auth_service.register(
            user_data=user_data,
            ip_address=get_client_ip(request),
        )
        await db.commit()
        
        # Refresh to get all relationships
        user = await user_service.get_user(user.id)
        
        return UserRead(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            profile=user.profile,
            roles=user_service.get_user_roles(user),
        )
    except RegistrationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    Authenticate user and return JWT tokens.
    
    - Returns access_token (short-lived)
    - Returns refresh_token (long-lived)
    """
    auth_service = AuthService(db)
    
    try:
        tokens = await auth_service.login(
            email=login_data.email,
            password=login_data.password,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
        await db.commit()
        return tokens
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    Refresh access token using refresh token.
    """
    auth_service = AuthService(db)
    
    try:
        tokens = await auth_service.refresh_access_token(token_data.refresh_token)
        return tokens
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Log out current user.
    
    Note: With stateless JWT, this only logs the action.
    Client should discard tokens locally.
    """
    auth_service = AuthService(db)
    await auth_service.logout(
        user=current_user,
        ip_address=get_client_ip(request),
    )
    await db.commit()
