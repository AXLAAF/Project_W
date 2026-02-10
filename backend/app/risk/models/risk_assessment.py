"""
Risk Assessment model for tracking student academic risk.
"""
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database import Base

if TYPE_CHECKING:
    from app.core.models.user import User
    from app.planning.models.group import Group


class RiskLevel(str, Enum):
    """Risk level classification."""
    LOW = "LOW"        # 0-30
    MEDIUM = "MEDIUM"  # 31-60
    HIGH = "HIGH"      # 61-80
    CRITICAL = "CRITICAL"  # 81-100


class RiskFactor(str, Enum):
    """Factors that contribute to risk score."""
    ATTENDANCE = "ATTENDANCE"
    GRADES = "GRADES"
    ASSIGNMENTS = "ASSIGNMENTS"
    PARTICIPATION = "PARTICIPATION"
    PREVIOUS_FAILURES = "PREVIOUS_FAILURES"


class RiskAssessment(Base):
    """Risk assessment for a student in a specific course."""

    __tablename__ = "risk_assessments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-100
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Individual factor scores
    attendance_score: Mapped[int] = mapped_column(Integer, default=0)  # 0-100 (higher = worse)
    grades_score: Mapped[int] = mapped_column(Integer, default=0)
    assignments_score: Mapped[int] = mapped_column(Integer, default=0)
    
    # Factor breakdown as JSON
    factor_details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    student: Mapped["User"] = relationship("User", foreign_keys=[student_id])
    group: Mapped["Group"] = relationship("Group")

    @classmethod
    def calculate_risk_level(cls, score: int) -> RiskLevel:
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
        return self.risk_level in (RiskLevel.HIGH.value, RiskLevel.CRITICAL.value)

    def __repr__(self) -> str:
        return f"<RiskAssessment(student={self.student_id}, score={self.risk_score}, level={self.risk_level})>"
