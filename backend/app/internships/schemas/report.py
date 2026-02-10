"""
InternshipReport Pydantic schemas for request/response validation.
"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.internships.models.internship_report import ReportStatus


class ReportCreate(BaseModel):
    """Schema for creating a report."""
    internship_id: int
    month_number: int = Field(..., ge=1, le=12)
    report_date: date
    hours_worked: int = Field(..., ge=0)
    activities_summary: Optional[str] = None
    achievements: Optional[str] = None
    challenges: Optional[str] = None


class ReportUpdate(BaseModel):
    """Schema for updating a report."""
    hours_worked: Optional[int] = Field(None, ge=0)
    activities_summary: Optional[str] = None
    achievements: Optional[str] = None
    challenges: Optional[str] = None
    file_path: Optional[str] = Field(None, max_length=500)


class ReportSubmit(BaseModel):
    """Schema for submitting a report for review."""
    pass  # Just changes status to SUBMITTED


class ReportReview(BaseModel):
    """Schema for reviewing a report (supervisor/admin)."""
    status: ReportStatus
    supervisor_comments: Optional[str] = None
    supervisor_grade: Optional[float] = Field(None, ge=0, le=100)


class ReportRead(BaseModel):
    """Schema for reading a report."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    internship_id: int
    month_number: int
    report_date: date
    file_path: Optional[str] = None
    hours_worked: int
    activities_summary: Optional[str] = None
    achievements: Optional[str] = None
    challenges: Optional[str] = None
    supervisor_comments: Optional[str] = None
    supervisor_grade: Optional[float] = None
    status: ReportStatus
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
