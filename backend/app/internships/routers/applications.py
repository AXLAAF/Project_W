"""
Applications API router.
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User
from app.dependencies import get_current_active_user
from app.shared.database import get_db
from app.internships.models.internship_application import ApplicationStatus
from app.internships.services.application_service import ApplicationService, ApplicationError
from app.internships.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationRead,
    ApplicationWithDetails,
)

router = APIRouter(prefix="/internships", tags=["applications"])


@router.post("/apply", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
async def apply_to_position(
    data: ApplicationCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ApplicationRead:
    """
    Apply to an internship position.
    """
    service = ApplicationService(db)
    try:
        # TODO: Get actual GPA and credits from user profile/academic history
        application = await service.apply(
            user=current_user,
            data=data,
            user_gpa=None,
            user_credits=None,
        )
        await db.commit()
        return ApplicationRead.model_validate(application)
    except ApplicationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/my-applications", response_model=list[ApplicationWithDetails])
async def get_my_applications(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[ApplicationStatus] = Query(None),
) -> list[ApplicationWithDetails]:
    """
    Get current user's applications.
    """
    service = ApplicationService(db)
    applications, _ = await service.get_by_user(
        user_id=current_user.id,
        offset=offset,
        limit=limit,
        status=status,
    )
    return [ApplicationWithDetails.model_validate(a) for a in applications]


@router.get("/applications", response_model=list[ApplicationWithDetails])
async def list_applications(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[ApplicationStatus] = Query(None),
    position_id: Optional[int] = Query(None),
) -> list[ApplicationWithDetails]:
    """
    List all applications (for reviewer/admin).
    """
    # TODO: Add role check for reviewer/admin
    service = ApplicationService(db)
    applications, _ = await service.get_all(
        offset=offset,
        limit=limit,
        status=status,
        position_id=position_id,
    )
    return [ApplicationWithDetails.model_validate(a) for a in applications]


@router.get("/applications/{application_id}", response_model=ApplicationWithDetails)
async def get_application(
    application_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ApplicationWithDetails:
    """
    Get application details by ID.
    """
    service = ApplicationService(db)
    application = await service.get_by_id(application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    # Check if user owns this application or is a reviewer
    # TODO: Add role check
    return ApplicationWithDetails.model_validate(application)


@router.put("/applications/{application_id}/approve", response_model=ApplicationRead)
async def approve_application(
    application_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    notes: Optional[str] = Query(None),
) -> ApplicationRead:
    """
    Approve an application (reviewer/admin).
    """
    # TODO: Add role check for reviewer/admin
    service = ApplicationService(db)
    try:
        application = await service.approve(
            application_id=application_id,
            reviewer_id=current_user.id,
            notes=notes,
        )
        await db.commit()
        return ApplicationRead.model_validate(application)
    except ApplicationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/applications/{application_id}/reject", response_model=ApplicationRead)
async def reject_application(
    application_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    notes: Optional[str] = Query(None),
) -> ApplicationRead:
    """
    Reject an application (reviewer/admin).
    """
    # TODO: Add role check for reviewer/admin
    service = ApplicationService(db)
    try:
        application = await service.reject(
            application_id=application_id,
            reviewer_id=current_user.id,
            notes=notes,
        )
        await db.commit()
        return ApplicationRead.model_validate(application)
    except ApplicationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_application(
    application_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> None:
    """
    Cancel own application.
    """
    service = ApplicationService(db)
    try:
        await service.cancel(application_id, current_user.id)
        await db.commit()
    except ApplicationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
