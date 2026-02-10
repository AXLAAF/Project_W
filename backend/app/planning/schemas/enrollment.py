"""Pydantic schemas for Enrollment and Academic History."""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict

from app.planning.models.enrollment import EnrollmentStatus


class EnrollmentCreate(BaseModel):
    """Schema for creating an Enrollment."""
    group_id: int


class EnrollmentUpdate(BaseModel):
    """Schema for updating an Enrollment."""
    status: Optional[str] = None
    grade: Optional[Decimal] = Field(default=None, ge=0, le=10)


class EnrollmentRead(BaseModel):
    """Schema for reading an Enrollment."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    group_id: int
    status: str
    grade: Optional[Decimal] = None
    grade_letter: Optional[str] = None
    attempt_number: int
    enrolled_at: datetime
    completed_at: Optional[datetime] = None


class SubjectBrief(BaseModel):
    """Brief subject info for history."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    credits: int


class PeriodBrief(BaseModel):
    """Brief period info for history."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str


class AcademicHistoryItem(BaseModel):
    """Schema for a single item in academic history."""
    model_config = ConfigDict(from_attributes=True)

    enrollment_id: int
    subject: SubjectBrief
    period: PeriodBrief
    group_number: str
    status: str
    grade: Optional[Decimal] = None
    grade_letter: Optional[str] = None
    attempt_number: int
    credits_earned: int  # 0 if not passed


class AcademicHistorySummary(BaseModel):
    """Summary of student's academic history."""
    student_id: int
    total_credits_attempted: int
    total_credits_earned: int
    gpa: float = Field(description="Grade Point Average on 0-10 scale")
    subjects_passed: int
    subjects_failed: int
    subjects_in_progress: int
    current_enrollments: List[AcademicHistoryItem] = Field(default_factory=list)
    history: List[AcademicHistoryItem] = Field(default_factory=list)


class SimulationRequest(BaseModel):
    """Request schema for enrollment simulation."""
    group_ids: List[int] = Field(..., min_length=1, max_length=10)


class ScheduleConflict(BaseModel):
    """Schema for schedule conflict."""
    group1_id: int
    group2_id: int
    day: str
    time_overlap: str
    message: str


class SimulationResult(BaseModel):
    """Result of enrollment simulation."""
    is_valid: bool
    total_credits: int
    conflicts: List[ScheduleConflict] = Field(default_factory=list)
    prerequisite_issues: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
