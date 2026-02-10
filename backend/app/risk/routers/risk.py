"""Risk API router."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database import get_db
from app.dependencies import get_current_user, require_role
from app.core.models.user import User
from app.risk.schemas.risk import (
    AttendanceCreate,
    AttendanceStats,
    GradeCreate,
    RiskAssessmentRead,
    StudentRiskSummary,
    GroupRiskDashboard,
)
from app.risk.services.risk_calculator import RiskCalculatorService
from app.risk.repositories.risk_repository import RiskRepository

router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("/my-risk/{group_id}", response_model=StudentRiskSummary)
async def get_my_risk_summary(
    group_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> StudentRiskSummary:
    """Get risk summary for the current user in a specific group."""
    service = RiskCalculatorService(db)
    summary = await service.get_student_risk_summary(current_user.id, group_id)
    return StudentRiskSummary(**summary)


@router.get("/student/{student_id}/group/{group_id}", response_model=StudentRiskSummary)
async def get_student_risk_summary(
    student_id: int,
    group_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(["PROFESOR", "COORDINADOR", "ADMIN_SISTEMA"]))],
) -> StudentRiskSummary:
    """Get risk summary for a specific student. Requires professor/coordinator role."""
    service = RiskCalculatorService(db)
    summary = await service.get_student_risk_summary(student_id, group_id)
    return StudentRiskSummary(**summary)


@router.post("/calculate/{student_id}/group/{group_id}", response_model=RiskAssessmentRead)
async def calculate_risk(
    student_id: int,
    group_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(["PROFESOR", "COORDINADOR", "ADMIN_SISTEMA"]))],
) -> RiskAssessmentRead:
    """Force recalculation of risk for a student. Requires professor/coordinator role."""
    service = RiskCalculatorService(db)
    assessment = await service.calculate_risk(student_id, group_id)
    await db.commit()
    return RiskAssessmentRead.model_validate(assessment)


@router.get("/dashboard/{group_id}", response_model=GroupRiskDashboard)
async def get_group_risk_dashboard(
    group_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(["PROFESOR", "COORDINADOR", "ADMIN_SISTEMA"]))],
) -> GroupRiskDashboard:
    """Get risk dashboard for a group. Requires professor/coordinator role."""
    service = RiskCalculatorService(db)
    dashboard = await service.get_group_risk_dashboard(group_id)
    return GroupRiskDashboard(**dashboard)


@router.get("/attendance/{student_id}/group/{group_id}", response_model=AttendanceStats)
async def get_attendance_stats(
    student_id: int,
    group_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AttendanceStats:
    """Get attendance statistics for a student."""
    # Students can only view their own stats
    if current_user.id != student_id:
        if not any(r.role.name in ["PROFESOR", "COORDINADOR", "ADMIN_SISTEMA"] for r in current_user.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other student's attendance",
            )

    repo = RiskRepository(db)
    stats = await repo.get_attendance_stats(student_id, group_id)
    return AttendanceStats(**stats)


@router.post("/attendance", status_code=status.HTTP_201_CREATED)
async def record_attendance(
    data: AttendanceCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(["PROFESOR", "COORDINADOR", "ADMIN_SISTEMA"]))],
) -> dict:
    """Record attendance for a student. Requires professor/coordinator role."""
    repo = RiskRepository(db)
    await repo.record_attendance(
        student_id=data.student_id,
        group_id=data.group_id,
        class_date=data.class_date,
        status=data.status,
        recorded_by=current_user.id,
        notes=data.notes,
    )
    await db.commit()
    return {"message": "Attendance recorded successfully"}


@router.post("/grade", status_code=status.HTTP_201_CREATED)
async def record_grade(
    data: GradeCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(["PROFESOR", "COORDINADOR", "ADMIN_SISTEMA"]))],
) -> dict:
    """Record a grade for a student. Requires professor/coordinator role."""
    repo = RiskRepository(db)
    await repo.record_grade(
        student_id=data.student_id,
        group_id=data.group_id,
        grade_type=data.grade_type,
        name=data.name,
        grade=data.grade,
        recorded_by=current_user.id,
        max_grade=data.max_grade,
        weight=data.weight,
        feedback=data.feedback,
    )
    await db.commit()
    return {"message": "Grade recorded successfully"}


@router.get("/at-risk-students/{group_id}")
async def get_at_risk_students(
    group_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(["PROFESOR", "COORDINADOR", "ADMIN_SISTEMA"]))],
) -> dict:
    """Get list of at-risk students in a group."""
    repo = RiskRepository(db)
    from app.risk.models.risk_assessment import RiskLevel
    
    at_risk = await repo.get_at_risk_students(group_id, RiskLevel.MEDIUM)
    
    return {
        "total": len(at_risk),
        "students": [
            {
                "student_id": a.student_id,
                "risk_score": a.risk_score,
                "risk_level": a.risk_level,
                "recommendation": a.recommendation,
            }
            for a in at_risk
        ],
    }
