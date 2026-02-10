"""
InternshipApplication Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, List, Any

from pydantic import BaseModel, Field, ConfigDict

from app.internships.models.internship_application import ApplicationStatus


class ApplicationCreate(BaseModel):
    """Schema for creating an application."""
    position_id: int
    cv_path: Optional[str] = Field(None, max_length=500)
    cover_letter: Optional[str] = None
    additional_documents: Optional[dict[str, Any]] = None


class ApplicationUpdate(BaseModel):
    """Schema for updating an application status (reviewer)."""
    status: ApplicationStatus
    reviewer_notes: Optional[str] = None


class ApplicationRead(BaseModel):
    """Schema for reading an application."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    position_id: int
    status: ApplicationStatus
    cv_path: Optional[str] = None
    cover_letter: Optional[str] = None
    additional_documents: Optional[dict[str, Any]] = None
    applied_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewer_id: Optional[int] = None
    reviewer_notes: Optional[str] = None


class UserSummary(BaseModel):
    """Summary of user for application listing."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: str


class PositionSummary(BaseModel):
    """Summary of position for application listing."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    company_id: int


class ApplicationWithDetails(ApplicationRead):
    """Application with user and position details."""
    user: UserSummary
    position: PositionSummary
