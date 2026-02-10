"""Enrollments API router."""
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database import get_db
from app.dependencies import get_current_user
from app.core.models.user import User
from app.planning.schemas.enrollment import (
    EnrollmentCreate,
    EnrollmentRead,
    AcademicHistorySummary,
    SimulationRequest,
    SimulationResult,
)
from app.planning.services.enrollment_service import (
    EnrollmentService,
    EnrollmentError,
    GroupFullError,
    AlreadyEnrolledError,
)
from app.planning.services.simulation_service import SimulationService

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.get("/current", response_model=List[EnrollmentRead])
async def get_current_enrollments(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> List[EnrollmentRead]:
    """Get current active enrollments for the authenticated student."""
    service = EnrollmentService(db)
    enrollments = await service.get_current_enrollments(current_user.id)
    return [EnrollmentRead.model_validate(e) for e in enrollments]


@router.get("/history", response_model=AcademicHistorySummary)
async def get_academic_history(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AcademicHistorySummary:
    """Get complete academic history for the authenticated student."""
    service = EnrollmentService(db)
    return await service.get_history(current_user.id)


@router.post("", response_model=EnrollmentRead, status_code=status.HTTP_201_CREATED)
async def enroll_in_group(
    data: EnrollmentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> EnrollmentRead:
    """Enroll in a group."""
    service = EnrollmentService(db)
    try:
        enrollment = await service.enroll(current_user.id, data.group_id)
        await db.commit()
        return EnrollmentRead.model_validate(enrollment)
    except GroupFullError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except AlreadyEnrolledError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except EnrollmentError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def drop_enrollment(
    enrollment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Drop an enrollment."""
    service = EnrollmentService(db)
    try:
        await service.drop(current_user.id, enrollment_id)
        await db.commit()
    except EnrollmentError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/simulate", response_model=SimulationResult)
async def simulate_enrollment(
    request: SimulationRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SimulationResult:
    """
    Simulate an enrollment scenario.
    
    Returns potential conflicts, prerequisite issues, and warnings
    without actually enrolling.
    """
    service = SimulationService(db)
    return await service.simulate_enrollment(current_user.id, request)


@router.get("/available-groups")
async def get_available_groups_for_student(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    period_id: int,
) -> dict:
    """
    Get groups available for the student based on:
    - Prerequisites met
    - Not already passed
    - Has available spots
    """
    service = SimulationService(db)
    return await service.get_available_groups_for_student(current_user.id, period_id)
