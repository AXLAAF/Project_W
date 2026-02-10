"""Risk schemas package."""
from app.risk.schemas.risk import (
    AttendanceRecord,
    AttendanceCreate,
    AttendanceStats,
    GradeRecord,
    GradeCreate,
    RiskAssessmentRead,
    RiskFactorDetail,
    StudentRiskSummary,
    GroupRiskDashboard,
    AtRiskStudent,
)

__all__ = [
    "AttendanceRecord",
    "AttendanceCreate",
    "AttendanceStats",
    "GradeRecord",
    "GradeCreate",
    "RiskAssessmentRead",
    "RiskFactorDetail",
    "StudentRiskSummary",
    "GroupRiskDashboard",
    "AtRiskStudent",
]
