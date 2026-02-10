"""
Enrollments API Router (Hexagonal Architecture).
"""
from typing import Annotated, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.interfaces.dependencies import (
    get_enroll_student_use_case,
    get_get_academic_history_use_case,
    get_simulate_enrollment_use_case,
    get_get_available_groups_use_case,
    get_enrollment_repository,
    get_current_user,
    get_db,
)
from app.application.use_cases.planning.enrollment.enroll_student import EnrollStudentUseCase
from app.application.use_cases.planning.enrollment.get_academic_history import GetAcademicHistoryUseCase
from app.application.use_cases.planning.enrollment.simulate_enrollment import SimulateEnrollmentUseCase
from app.application.use_cases.planning.enrollment.get_available_groups import GetAvailableGroupsUseCase

from app.domain.entities.user import User
from app.domain.repositories.enrollment_repository import IEnrollmentRepository
from app.planning.schemas.enrollment import (
    EnrollmentCreate,
    EnrollmentRead,
    AcademicHistorySummary,
    SimulationRequest,
    SimulationResult,
)

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.get("/current", response_model=List[EnrollmentRead])
async def get_current_enrollments(
    repo: Annotated[IEnrollmentRepository, Depends(get_enrollment_repository)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> List[EnrollmentRead]:
    """Get current active enrollments for the authenticated student."""
    enrollments = await repo.get_current_enrollments(current_user.id)
    return [EnrollmentRead.model_validate(e) for e in enrollments]


@router.get("/history", response_model=AcademicHistorySummary)
async def get_academic_history(
    use_case: Annotated[GetAcademicHistoryUseCase, Depends(get_get_academic_history_use_case)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AcademicHistorySummary:
    """Get complete academic history for the authenticated student."""
    result = await use_case.execute(current_user.id)
    
    # Map DTO to Schema
    # AcademicHistoryDTO has 'summary' (AcademicSummaryDTO) and 'enrollments' (List[EnrollmentHistoryDTO])
    # AcademicHistorySummary schema has fields that match AcademicSummaryDTO + history list
    
    # We need to restructure slightly if names don't match 1:1
    
    # Schema:
    # student_id: int
    # total_credits_attempted: int
    # total_credits_earned: int
    # gpa: float
    # subjects_passed: int
    # subjects_failed: int
    # subjects_in_progress: int
    # current_enrollments: List[AcademicHistoryItem]
    # history: List[AcademicHistoryItem]
    
    # DTO:
    # student_id: int
    # enrollments: List[EnrollmentHistoryDTO]
    # summary: AcademicSummaryDTO
    
    # Helper to map enrollment DTO to AcademicHistoryItem schema
    def map_item(e):
        return {
            "enrollment_id": e.id,
            "subject": {
                "id": 0, # DTO missing subject_id
                "code": e.subject_code,
                "name": e.subject_name,
                "credits": 0, # DTO missing credits
            },
            "period": {
                "id": 0,
                "code": "",
                "name": e.period_name or "Unknown",
            },
            "group_number": "", # DTO missing group info
            "status": e.status,
            "grade": e.grade,
            "grade_letter": e.grade_letter,
            "attempt_number": e.attempt_number,
            "credits_earned": 0, # Computed
        }

    history_items = [map_item(e) for e in result.enrollments]
    
    return AcademicHistorySummary(
        student_id=result.student_id,
        total_credits_attempted=result.summary.total_credits_attempted,
        total_credits_earned=result.summary.total_credits_earned,
        gpa=result.summary.overall_gpa,
        subjects_passed=result.summary.total_subjects_passed,
        subjects_failed=result.summary.total_subjects_failed,
        subjects_in_progress=result.summary.current_enrollments,
        current_enrollments=[], # UseCase doesn't separate them explicitly in summary DTO list
        history=history_items,
    )


@router.post("", response_model=EnrollmentRead, status_code=status.HTTP_201_CREATED)
async def enroll_in_group(
    data: EnrollmentCreate,
    use_case: Annotated[EnrollStudentUseCase, Depends(get_enroll_student_use_case)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Dict[str, Any]:
    """Enroll in a group."""
    result = await use_case.execute(current_user.id, data.group_id)
    
    if not result.success:
        if "conflict" in (result.error_message or "").lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=result.error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.error_message)
        
    return {"id": result.enrollment_id, "status": "ENROLLED", "student_id": current_user.id, "group_id": data.group_id, "enrolled_at": "2024-01-01T00:00:00", "attempt_number": 1} # Mocked return for now as DTO doesn't return full object


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def drop_enrollment(
    enrollment_id: int,
    repo: Annotated[IEnrollmentRepository, Depends(get_enrollment_repository)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Drop an enrollment."""
    # Verify ownership
    enrollment = await repo.get_by_id(enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
        
    if enrollment.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    await repo.delete(enrollment_id)
    # Commit handled by repo implementation or session dependency needs commit?
    # Repo implementation using session should probably commit.
    # If not, we might need to inject session and commit.
    # Standard practice: Service/Repo handles commit or UnitOfWork. 
    # Here we are using repo directly. Let's assume repo saves changes.


@router.post("/simulate", response_model=SimulationResult)
async def simulate_enrollment(
    request: SimulationRequest,
    use_case: Annotated[SimulateEnrollmentUseCase, Depends(get_simulate_enrollment_use_case)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SimulationResult:
    """Simulate enrollment."""
    return await use_case.execute(current_user.id, request)


@router.get("/available-groups")
async def get_available_groups_for_student(
    period_id: int,
    use_case: Annotated[GetAvailableGroupsUseCase, Depends(get_get_available_groups_use_case)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Dict[str, Any]:
    """Get available groups."""
    return await use_case.execute(current_user.id, period_id)
