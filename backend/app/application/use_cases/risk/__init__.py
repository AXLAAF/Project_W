"""Risk module use cases."""
from app.application.use_cases.risk.calculate_student_risk import CalculateStudentRiskUseCase
from app.application.use_cases.risk.get_risk_dashboard import GetRiskDashboardUseCase

__all__ = [
    "CalculateStudentRiskUseCase",
    "GetRiskDashboardUseCase",
]
