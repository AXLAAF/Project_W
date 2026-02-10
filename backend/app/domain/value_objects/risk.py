"""
Risk module value objects.
Immutable objects representing risk-related values.
"""
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, IntEnum
from typing import Optional


class RiskLevel(str, Enum):
    """Risk level classification."""
    LOW = "LOW"           # 0-30
    MEDIUM = "MEDIUM"     # 31-60
    HIGH = "HIGH"         # 61-80
    CRITICAL = "CRITICAL" # 81-100
    
    @classmethod
    def from_score(cls, score: int) -> "RiskLevel":
        """Calculate risk level from score."""
        if score <= 30:
            return cls.LOW
        elif score <= 60:
            return cls.MEDIUM
        elif score <= 80:
            return cls.HIGH
        else:
            return cls.CRITICAL
    
    @property
    def spanish_name(self) -> str:
        """Get Spanish name for the level."""
        names = {
            RiskLevel.LOW: "Bajo",
            RiskLevel.MEDIUM: "Medio",
            RiskLevel.HIGH: "Alto",
            RiskLevel.CRITICAL: "Crítico",
        }
        return names.get(self, "Desconocido")
    
    @property
    def color(self) -> str:
        """Get color code for the level."""
        colors = {
            RiskLevel.LOW: "#4CAF50",      # Green
            RiskLevel.MEDIUM: "#FFC107",   # Yellow
            RiskLevel.HIGH: "#FF9800",     # Orange
            RiskLevel.CRITICAL: "#F44336", # Red
        }
        return colors.get(self, "#9E9E9E")


class AttendanceStatus(str, Enum):
    """Attendance status classification."""
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    EXCUSED = "EXCUSED"
    
    @property
    def counts_as_present(self) -> bool:
        """Check if this status counts as being present."""
        return self in (AttendanceStatus.PRESENT, AttendanceStatus.LATE)
    
    @property
    def counts_as_absence(self) -> bool:
        """Check if this status counts as an absence."""
        return self == AttendanceStatus.ABSENT


class GradeType(str, Enum):
    """Type of grade evaluation."""
    EXAM = "EXAM"
    QUIZ = "QUIZ"
    PARTIAL = "PARTIAL"
    PROJECT = "PROJECT"
    HOMEWORK = "HOMEWORK"
    PARTICIPATION = "PARTICIPATION"
    FINAL = "FINAL"
    
    @property
    def spanish_name(self) -> str:
        """Get Spanish name for the grade type."""
        names = {
            GradeType.EXAM: "Examen",
            GradeType.QUIZ: "Quiz",
            GradeType.PARTIAL: "Parcial",
            GradeType.PROJECT: "Proyecto",
            GradeType.HOMEWORK: "Tarea",
            GradeType.PARTICIPATION: "Participación",
            GradeType.FINAL: "Final",
        }
        return names.get(self, "Otro")


class SubmissionStatus(str, Enum):
    """Status of an assignment submission."""
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    LATE = "LATE"
    GRADED = "GRADED"
    MISSING = "MISSING"
    
    @property
    def is_submitted(self) -> bool:
        """Check if the assignment was submitted."""
        return self in (
            SubmissionStatus.SUBMITTED,
            SubmissionStatus.LATE,
            SubmissionStatus.GRADED,
        )
    
    @property
    def is_complete(self) -> bool:
        """Check if the submission is complete (submitted or graded)."""
        return self in (SubmissionStatus.SUBMITTED, SubmissionStatus.GRADED)


@dataclass(frozen=True)
class RiskScore:
    """
    Risk score value object (0-100).
    Higher score = higher risk.
    """
    value: int
    
    def __post_init__(self):
        if not 0 <= self.value <= 100:
            raise ValueError(f"Risk score must be between 0 and 100, got {self.value}")
    
    @property
    def level(self) -> RiskLevel:
        """Get the risk level for this score."""
        return RiskLevel.from_score(self.value)
    
    @property
    def is_at_risk(self) -> bool:
        """Check if this score indicates at-risk status."""
        return self.level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
    
    @property
    def percentage(self) -> int:
        """Get score as percentage."""
        return self.value
    
    def __int__(self) -> int:
        return self.value
    
    def __str__(self) -> str:
        return f"{self.value}%"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, RiskScore):
            return self.value == other.value
        if isinstance(other, int):
            return self.value == other
        return False
    
    def __lt__(self, other) -> bool:
        if isinstance(other, RiskScore):
            return self.value < other.value
        if isinstance(other, int):
            return self.value < other
        return NotImplemented
    
    def __hash__(self) -> int:
        return hash(self.value)


class RiskFactor(str, Enum):
    """Factors that contribute to risk score."""
    ATTENDANCE = "ATTENDANCE"
    GRADES = "GRADES"
    ASSIGNMENTS = "ASSIGNMENTS"
    PARTICIPATION = "PARTICIPATION"
    PREVIOUS_FAILURES = "PREVIOUS_FAILURES"
