"""
Users API router.
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User
from app.core.schemas.user import ProfileUpdate, UserRead, UserUpdate
from app.core.services.user_service import UserService, UserNotFoundError
from app.dependencies import (
    get_client_ip,
    get_current_active_user,
    require_admin,
    require_coordinator,
)
from app.shared.database import get_db
from app.shared.pagination import PaginatedResponse

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    """Get current authenticated user's profile."""
    user_service = UserService(db)
    return UserRead(
        id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        profile=current_user.profile,
        roles=user_service.get_user_roles(current_user),
    )


@router.put("/me", response_model=UserRead)
async def update_current_user_profile(
    request: Request,
    profile_data: ProfileUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    """Update current user's profile."""
    user_service = UserService(db)
    
    user = await user_service.update_profile(
        user=current_user,
        profile_data=profile_data,
        ip_address=get_client_ip(request),
    )
    await db.commit()
    
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


@router.get("", response_model=PaginatedResponse[UserRead])
async def list_users(
    current_user: Annotated[User, Depends(require_coordinator)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
) -> PaginatedResponse[UserRead]:
    """
    List all users (admin/coordinator only).
    
    Supports pagination and filtering by active status.
    """
    user_service = UserService(db)
    users, total = await user_service.list_users(
        page=page,
        page_size=page_size,
        is_active=is_active,
    )
    
    user_reads = [
        UserRead(
            id=u.id,
            email=u.email,
            is_active=u.is_active,
            is_verified=u.is_verified,
            created_at=u.created_at,
            updated_at=u.updated_at,
            profile=u.profile,
            roles=user_service.get_user_roles(u),
        )
        for u in users
    ]
    
    return PaginatedResponse.create(
        items=user_reads,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    current_user: Annotated[User, Depends(require_coordinator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    """Get user by ID (admin/coordinator only)."""
    user_service = UserService(db)
    
    try:
        user = await user_service.get_user(user_id)
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
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    request: Request,
    user_id: int,
    user_data: UserUpdate,
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    """Update user (admin only)."""
    user_service = UserService(db)
    
    try:
        user = await user_service.update_user(
            user_id=user_id,
            user_data=user_data,
            updated_by=current_user.id,
            ip_address=get_client_ip(request),
        )
        await db.commit()
        
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
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    request: Request,
    user_id: int,
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Deactivate user (admin only). Does not delete, just sets is_active=False."""
    user_service = UserService(db)
    
    try:
        await user_service.deactivate_user(
            user_id=user_id,
            deactivated_by=current_user.id,
            ip_address=get_client_ip(request),
        )
        await db.commit()
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/{user_id}/roles/{role_name}", response_model=UserRead)
async def assign_role(
    request: Request,
    user_id: int,
    role_name: str,
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    """Assign a role to a user (admin only)."""
    user_service = UserService(db)
    
    try:
        user = await user_service.assign_role_to_user(
            user_id=user_id,
            role_name=role_name.upper(),
            assigned_by=current_user.id,
            ip_address=get_client_ip(request),
        )
        await db.commit()
        
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
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/{user_id}/roles/{role_name}", response_model=UserRead)
async def remove_role(
    request: Request,
    user_id: int,
    role_name: str,
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    """Remove a role from a user (admin only)."""
    user_service = UserService(db)
    
    try:
        user = await user_service.remove_role_from_user(
            user_id=user_id,
            role_name=role_name.upper(),
            removed_by=current_user.id,
            ip_address=get_client_ip(request),
        )
        await db.commit()
        
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
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
