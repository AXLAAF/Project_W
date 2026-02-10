"""
Calculate Risk Score Use Case.
Orchestrates data gathering, ML prediction, and result persistence.
"""
from datetime import datetime
from typing import Optional

from app.domain.repositories.risk_repository import IRiskRepository
from app.domain.ports.risk_model_port import IRiskModelPort
from app.domain.entities.risk.risk_assessment import RiskAssessment, RiskLevel
from app.application.dtos.risk_dtos import RiskAssessmentDTO, RiskPredictionRequestDTO


class CalculateRiskScoreUseCase:
    """
    Use case to calculate and save risk score for a student.
    """
    
    def __init__(
        self,
        risk_repo: IRiskRepository,
        risk_model: IRiskModelPort
    ):
        self._risk_repo = risk_repo
        self._risk_model = risk_model
    
    async def execute(self, request: RiskPredictionRequestDTO) -> RiskAssessmentDTO:
        # 1. Gather data
        # In a real scenario, we would inject repositories for Grades and Attendance here
        # and fetch the actual data for the student.
        # For this refactoring phase, we'll use the DTO values or defaults/mock data
        
        features = {
            "attendance_rate": request.attendance_rate if request.attendance_rate is not None else 85.0,
            "average_grade": request.average_grade if request.average_grade is not None else 75.0,
            "missed_assignments": request.missed_assignments if request.missed_assignments is not None else 1,
        }
        
        # 2. Predict using ML Model Port
        score, factors = await self._risk_model.predict_risk(features)
        
        # 3. Create Domain Entity
        level = RiskAssessment.calculate_level(score)
        
        recommendation = self._generate_recommendation(level, factors)
        
        assessment = RiskAssessment(
            student_id=request.student_id,
            group_id=request.group_id,
            risk_score=score,
            risk_level=level,
            attendance_score=int(100 - features["attendance_rate"]), # Simplified mapping
            grades_score=int(100 - features["average_grade"]),
            assignments_score=features["missed_assignments"] * 10,
            factor_details=factors,
            recommendation=recommendation,
        )
        
        # 4. Persist
        saved_assessment = await self._risk_repo.save(assessment)
        
        # 5. Return DTO
        return self._to_dto(saved_assessment)

    def _generate_recommendation(self, level: RiskLevel, factors: dict) -> str:
        if level == RiskLevel.LOW:
            return "Keep up the good work."
        elif level == RiskLevel.MEDIUM:
            return "Monitor attendance and upcoming assignments."
        else:
            reasons = ", ".join(factors.keys())
            return f"Immediate intervention required. Key factors: {reasons}"

    def _to_dto(self, entity: RiskAssessment) -> RiskAssessmentDTO:
        return RiskAssessmentDTO(
            id=entity.id if entity.id else 0,
            student_id=entity.student_id,
            group_id=entity.group_id,
            risk_score=entity.risk_score,
            risk_level=entity.risk_level,
            attendance_score=entity.attendance_score,
            grades_score=entity.grades_score,
            assignments_score=entity.assignments_score,
            factor_details=entity.factor_details,
            recommendation=entity.recommendation,
            assessed_at=entity.assessed_at if entity.assessed_at else datetime.now()
        )
