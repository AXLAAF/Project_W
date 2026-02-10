"""
Risk API Router (Hexagonal Architecture).
"""
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.interfaces.dependencies import (
    get_calculate_risk_score_use_case,
    get_risk_history_use_case,
    get_group_risk_statistics_use_case,
    require_roles,
)
from app.application.use_cases.risk.calculate_risk import CalculateRiskScoreUseCase
# from app.application.use_cases.risk.get_history import GetRiskHistoryUseCase
# from app.application.use_cases.risk.get_group_statistics import GetGroupRiskStatisticsUseCase
from app.application.dtos.risk_dtos import RiskAssessmentDTO, RiskPredictionRequestDTO
from app.domain.entities.user import User


router = APIRouter(prefix="/risk", tags=["risk"])


@router.post("/calculate", response_model=RiskAssessmentDTO)
async def calculate_risk(
    request: RiskPredictionRequestDTO,
    use_case: Annotated[CalculateRiskScoreUseCase, Depends(get_calculate_risk_score_use_case)],
    current_user: Annotated[User, Depends(require_roles(["PROFESOR", "COORDINADOR", "ADMIN_SISTEMA"]))],
) -> RiskAssessmentDTO:
    """
    Calculate and save risk score for a student.
    Requires PROFESOR, COORDINADOR, or ADMIN_SISTEMA role.
    """
    try:
        return await use_case.execute(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/history/student/{student_id}", response_model=List[RiskAssessmentDTO])
async def get_student_risk_history(
    student_id: int,
    # use_case: Annotated[GetRiskHistoryUseCase, Depends(get_risk_history_use_case)],
    current_user: Annotated[User, Depends(require_roles(["PROFESOR", "COORDINADOR", "ADMIN_SISTEMA", "ALUMNO"]))],
    limit: int = Query(10, ge=1, le=50),
) -> List[RiskAssessmentDTO]:
    """
    Get risk assessment history for a student.
    Students can only view their own history.
    """
    # Authorization check for students viewing other students
    if "ALUMNO" in current_user.roles and current_user.id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view risk history of other students",
        )
        
    # Placeholder for now until use case is implemented
    return []
