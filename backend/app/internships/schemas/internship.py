"""
Internship Pydantic schemas for request/response validation.
"""
from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.internships.models.internship import InternshipStatus


class InternshipCreate(BaseModel):
    """Schema for creating an internship (after application approval)."""
    application_id: int
    start_date: date
    expected_end_date: date
    supervisor_name: str = Field(..., min_length=1, max_length=200)
    supervisor_email: EmailStr
    supervisor_phone: Optional[str] = Field(None, max_length=20)


class InternshipUpdate(BaseModel):
    """Schema for updating an internship."""
    supervisor_name: Optional[str] = Field(None, min_length=1, max_length=200)
    supervisor_email: Optional[EmailStr] = None
    supervisor_phone: Optional[str] = Field(None, max_length=20)
    status: Optional[InternshipStatus] = None
    actual_end_date: Optional[date] = None
    final_grade: Optional[float] = Field(None, ge=0, le=100)


class InternshipComplete(BaseModel):
    """Schema for completing an internship."""
    actual_end_date: date
    final_grade: float = Field(..., ge=0, le=100)
    total_hours: int = Field(..., ge=0)


class InternshipRead(BaseModel):
    """Schema for reading an internship."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    application_id: int
    start_date: date
    expected_end_date: date
    actual_end_date: Optional[date] = None
    status: InternshipStatus
    supervisor_name: str
    supervisor_email: str
    supervisor_phone: Optional[str] = None
    total_hours: int
    final_grade: Optional[float] = None
    completion_certificate_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ReportSummary(BaseModel):
    """Summary of report for internship listing."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    month_number: int
    status: str
    hours_worked: int


class InternshipWithReports(InternshipRead):
    """Internship with report summaries."""
    reports: List[ReportSummary] = []
