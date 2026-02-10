"""Pydantic schemas for Risk module."""
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class AttendanceCreate(BaseModel):
    """Schema for recording attendance."""
    student_id: int
    group_id: int
    class_date: date
    status: str = Field(..., pattern="^(PRESENT|ABSENT|LATE|EXCUSED)$")
    notes: Optional[str] = None


class AttendanceRecord(BaseModel):
    """Schema for reading attendance."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    group_id: int
    class_date: date
    status: str
    notes: Optional[str] = None
    created_at: datetime


class AttendanceStats(BaseModel):
    """Attendance statistics summary."""
    total_classes: int
    present: int
    absent: int
    late: int
    excused: int
    attendance_rate: float


class GradeCreate(BaseModel):
    """Schema for recording a grade."""
    student_id: int
    group_id: int
    grade_type: str = Field(..., pattern="^(EXAM|QUIZ|PARTIAL|PROJECT|HOMEWORK|PARTICIPATION|FINAL)$")
    name: str = Field(..., min_length=1, max_length=100)
    grade: float = Field(..., ge=0, le=100)
    max_grade: float = Field(default=10.0, ge=0)
    weight: float = Field(default=1.0, ge=0)
    feedback: Optional[str] = None


class GradeRecord(BaseModel):
    """Schema for reading a grade."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    group_id: int
    grade_type: str
    name: str
    grade: float
    max_grade: float
    weight: float
    normalized_grade: float
    is_passing: bool
    feedback: Optional[str] = None
    graded_at: datetime


class RiskFactorDetail(BaseModel):
    """Detail of a single risk factor."""
    score: int
    # Additional fields depend on factor type
    data: Optional[dict] = None


class RiskAssessmentRead(BaseModel):
    """Schema for reading a risk assessment."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    group_id: int
    risk_score: int
    risk_level: str
    attendance_score: int
    grades_score: int
    assignments_score: int
    factor_details: Optional[dict] = None
    recommendation: Optional[str] = None
    assessed_at: datetime


class StudentRiskSummary(BaseModel):
    """Summary of a student's risk status."""
    current_score: int
    risk_level: str
    is_at_risk: bool
    trend: str  # "stable", "increasing", "decreasing"
    factors: Optional[dict] = None
    recommendation: Optional[str] = None
    last_assessed: str


class AtRiskStudent(BaseModel):
    """Schema for an at-risk student in dashboard."""
    student_id: int
    student_name: str
    risk_score: int
    main_factor: Optional[str] = None


class GroupRiskDashboard(BaseModel):
    """Risk dashboard for a group."""
    total_at_risk: int
    critical_count: int
    high_count: int
    medium_count: int
    critical_students: List[AtRiskStudent] = Field(default_factory=list)
    high_students: List[AtRiskStudent] = Field(default_factory=list)
