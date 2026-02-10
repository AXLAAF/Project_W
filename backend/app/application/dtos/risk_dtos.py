"""
Risk Module DTOs.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional

from app.domain.entities.risk.risk_assessment import RiskLevel


@dataclass
class RiskAssessmentDTO:
    """DTO for risk assessment response."""
    id: int
    student_id: int
    group_id: int
    risk_score: int
    risk_level: RiskLevel
    attendance_score: int
    grades_score: int
    assignments_score: int
    factor_details: Dict[str, Any]
    recommendation: Optional[str]
    assessed_at: datetime
    
    @property
    def is_at_risk(self) -> bool:
        return self.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)


@dataclass
class RiskPredictionRequestDTO:
    """DTO for requesting a risk prediction."""
    student_id: int
    group_id: int
    # Optional manual overrides for simulation
    attendance_rate: Optional[float] = None
    average_grade: Optional[float] = None
    missed_assignments: Optional[int] = None
