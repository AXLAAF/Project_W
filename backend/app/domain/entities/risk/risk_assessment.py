"""
Risk Assessment Domain Entity.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class RiskLevel(str, Enum):
    """Risk level classification."""
    LOW = "LOW"        # 0-30
    MEDIUM = "MEDIUM"  # 31-60
    HIGH = "HIGH"      # 61-80
    CRITICAL = "CRITICAL"  # 81-100


@dataclass
class RiskAssessment:
    """Risk assessment domain entity."""
    student_id: int
    group_id: int
    risk_score: int
    risk_level: RiskLevel
    attendance_score: int = 0
    grades_score: int = 0
    assignments_score: int = 0
    factor_details: Dict[str, Any] = field(default_factory=dict)
    recommendation: Optional[str] = None
    id: Optional[int] = None
    assessed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    @classmethod
    def calculate_level(cls, score: int) -> RiskLevel:
        """Calculate risk level from score."""
        if score <= 30:
            return RiskLevel.LOW
        elif score <= 60:
            return RiskLevel.MEDIUM
        elif score <= 80:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    @property
    def is_at_risk(self) -> bool:
        """Check if student is at high risk."""
        return self.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
