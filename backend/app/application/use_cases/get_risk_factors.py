"""
Get Risk Factors use case.
Retrieves and explains risk factors for a student.
"""
from typing import List, Dict, Any, Optional

from app.domain.repositories.risk_repository import IRiskAssessmentRepository
from app.domain.entities.risk.risk_assessment import RiskAssessment


class GetRiskFactorsUseCase:
    """
    Use case: Get risk factors and explanation.
    """
    
    def __init__(self, risk_repo: IRiskAssessmentRepository):
        self.risk_repo = risk_repo
        
    async def execute(self, student_id: int, group_id: int) -> Dict[str, Any]:
        """
        Get latest risk assessment and explain it.
        """
        assessment = await self.risk_repo.get_latest(student_id, group_id)
        
        if not assessment:
            return {
                "has_data": False,
                "risk_level": "UNKNOWN",
                "risk_score": 0,
                "factors": []
            }
            
        factors = []
        if assessment.factor_details and "factors" in assessment.factor_details:
             factors = assessment.factor_details["factors"]
        else:
            # Fallback explanation if model didn't provide details or old data
            factors = [
                {
                    "name": "Attendance",
                    "score": assessment.attendance_score,
                    "status": "High Risk" if assessment.attendance_score > 60 else "Normal"
                },
                {
                    "name": "Grades",
                    "score": assessment.grades_score,
                    "status": "High Risk" if assessment.grades_score > 60 else "Normal"
                }
            ]
            
        return {
            "has_data": True,
            "risk_level": assessment.risk_level.value,
            "risk_score": assessment.risk_score.value,
            "assessed_at": assessment.assessed_at.isoformat() if assessment.assessed_at else None,
            "factors": factors,
            "recommendation": assessment.recommendation or "Monitor student progress."
        }
