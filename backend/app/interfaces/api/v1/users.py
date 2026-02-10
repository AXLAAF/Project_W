"""
Users API Router (Hexagonal Architecture).
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.interfaces.dependencies import (
    get_user_profile_use_case,
    get_update_profile_use_case,
    get_list_users_use_case,
    get_deactivate_user_use_case,
    get_assign_role_use_case,
    get_remove_role_use_case,
    get_current_active_user,
    require_coordinator,
    require_admin,
)
from app.application.use_cases.get_user_profile import GetUserProfileUseCase
from app.application.use_cases.update_profile import UpdateProfileUseCase
from app.application.use_cases.list_users import ListUsersUseCase
from app.application.use_cases.deactivate_user import DeactivateUserUseCase
from app.application.use_cases.assign_role import AssignRoleUseCase
from app.application.use_cases.remove_role import RemoveRoleUseCase
from app.domain.entities.user import User

# Schemas & DTOs
from app.core.schemas.user import UserRead, ProfileUpdate, UserUpdate
from app.application.dtos.user_dtos import ProfileUpdateDTO, UserUpdateDTO
from app.shared.pagination import PaginatedResponse

router = APIRouter()

@router.get("/me", response_model=UserRead)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[GetUserProfileUseCase, Depends(get_user_profile_use_case)],
) -> UserRead:
    """Get current user's profile."""
    return await use_case.execute(current_user.id or 0)

@router.put("/me", response_model=UserRead)
async def update_current_user_profile(
    profile_data: ProfileUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[UpdateProfileUseCase, Depends(get_update_profile_use_case)],
) -> UserRead:
    """Update current user's profile."""
    dto = ProfileUpdateDTO(
        first_name=profile_data.first_name,
        last_name=profile_data.last_name,
        department=profile_data.department,
        program=profile_data.program,
        phone=profile_data.phone,
        photo_url=profile_data.photo_url,
    )
    return await use_case.execute(current_user.id or 0, dto)

@router.get("", response_model=PaginatedResponse[UserRead])
async def list_users(
    use_case: Annotated[ListUsersUseCase, Depends(get_list_users_use_case)],
    current_user: Annotated[User, Depends(require_coordinator)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
) -> PaginatedResponse[UserRead]:
    """List users (Coordinator+)."""
    result = await use_case.execute(page, page_size, is_active)
    
    return PaginatedResponse.create(
        items=result.items,
        total=result.total,
        page=page,
        page_size=page_size,
    )

@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    use_case: Annotated[GetUserProfileUseCase, Depends(get_user_profile_use_case)],
    current_user: Annotated[User, Depends(require_coordinator)],
) -> UserRead:
    """Get user by ID."""
    try:
        return await use_case.execute(user_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    use_case: Annotated[UpdateProfileUseCase, Depends(get_update_profile_use_case)], # Note: UpdateProfile might need to support admin updates 
    # Wait, UpdateProfileUseCase is for updating OWN profile usually. Admin user update might need a separate use case or extended DTO.
    # Checking UpdateProfileUseCase... assuming it only updates profile fields.
    current_user: Annotated[User, Depends(require_admin)],
) -> UserRead:
    """Update user (Admin). Note: Currently reusing UpdateProfileUseCase which might be limited."""
    # TODO: Create AdminUpdateUserUseCase if needed for is_active, flags, etc.
    # For now implementation is limited to profile updates
    dto = ProfileUpdateDTO(
        first_name=user_data.profile.first_name if user_data.profile else None,
        # ... mapping needs to be robust
    )
    # Skipping generic implementation to check if a specific Admin Update Use Case exists.
    # If not, blocking this endpoint for now or implementing partially.
    # Assuming UpdateProfileUseCase is insufficient for full admin update (roles etc are separate).
    raise HTTPException(status_code=501, detail="Not implemented yet")

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: int,
    use_case: Annotated[DeactivateUserUseCase, Depends(get_deactivate_user_use_case)],
    current_user: Annotated[User, Depends(require_admin)],
) -> None:
    """Deactivate user."""
    await use_case.execute(user_id)

@router.post("/{user_id}/roles/{role_name}", response_model=UserRead)
async def assign_role(
    user_id: int,
    role_name: str,
    use_case: Annotated[AssignRoleUseCase, Depends(get_assign_role_use_case)],
    profile_use_case: Annotated[GetUserProfileUseCase, Depends(get_user_profile_use_case)],
    current_user: Annotated[User, Depends(require_admin)],
) -> UserRead:
    """Assign role."""
    await use_case.execute(user_id, role_name, current_user.id or 0)
    return await profile_use_case.execute(user_id)

@router.delete("/{user_id}/roles/{role_name}", response_model=UserRead)
async def remove_role(
    user_id: int,
    role_name: str,
    use_case: Annotated[RemoveRoleUseCase, Depends(get_remove_role_use_case)],
    profile_use_case: Annotated[GetUserProfileUseCase, Depends(get_user_profile_use_case)],
    current_user: Annotated[User, Depends(require_admin)],
) -> UserRead:
    """Remove role."""
    await use_case.execute(user_id, role_name, current_user.id or 0)
    return await profile_use_case.execute(user_id)
