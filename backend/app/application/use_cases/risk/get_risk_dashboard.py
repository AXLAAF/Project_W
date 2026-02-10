"""
Get Risk Dashboard Use Case.
Retrieves risk summary for a group.
"""
from typing import Dict, List, Any

from app.domain.repositories.risk_repository import IRiskAssessmentRepository
from app.domain.value_objects.risk import RiskLevel


class GetRiskDashboardUseCase:
    """Use case for retrieving risk dashboard data."""

    def __init__(self, risk_repo: IRiskAssessmentRepository):
        self.risk_repo = risk_repo

    async def execute(self, group_id: int) -> Dict[str, Any]:
        """
        Get risk dashboard stats for a group.
        """
        # Get all students with at least LOW risk (basically everyone assessed)
        assessments = await self.risk_repo.get_at_risk_students(
            group_id, min_level=RiskLevel.LOW
        )

        total_assessed = len(assessments)
        critical = [a for a in assessments if a.risk_level == RiskLevel.CRITICAL]
        high = [a for a in assessments if a.risk_level == RiskLevel.HIGH]
        medium = [a for a in assessments if a.risk_level == RiskLevel.MEDIUM]
        low = [a for a in assessments if a.risk_level == RiskLevel.LOW]

        return {
            "summary": {
                "total_assessed": total_assessed,
                "critical": len(critical),
                "high": len(high),
                "medium": len(medium),
                "low": len(low),
            },
            "critical_students": [
                {
                    "student_id": a.student_id,
                    "risk_score": a.score_value,
                    "main_factor": a.main_risk_factor.value,
                    "recommendation": a.recommendation,
                }
                for a in critical
            ],
            "high_risk_students": [
                {
                    "student_id": a.student_id,
                    "risk_score": a.score_value,
                    "main_factor": a.main_risk_factor.value,
                }
                for a in high
            ],
        }
