"""
InternshipPosition Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.internships.models.internship_position import PositionModality


class PositionBase(BaseModel):
    """Base position schema with common fields."""
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=10)
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    duration_months: int = Field(default=6, ge=1, le=24)
    modality: PositionModality = PositionModality.PRESENCIAL
    location: Optional[str] = Field(None, max_length=255)
    min_gpa: Optional[float] = Field(None, ge=0, le=100)
    min_credits: Optional[int] = Field(None, ge=0)
    capacity: int = Field(default=1, ge=1)


class PositionCreate(PositionBase):
    """Schema for creating a position."""
    company_id: int


class PositionUpdate(BaseModel):
    """Schema for updating a position (all fields optional)."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    duration_months: Optional[int] = Field(None, ge=1, le=24)
    modality: Optional[PositionModality] = None
    location: Optional[str] = Field(None, max_length=255)
    min_gpa: Optional[float] = Field(None, ge=0, le=100)
    min_credits: Optional[int] = Field(None, ge=0)
    capacity: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class PositionRead(PositionBase):
    """Schema for reading a position."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    company_id: int
    filled_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    @property
    def available_spots(self) -> int:
        return self.capacity - self.filled_count


class CompanySummary(BaseModel):
    """Summary of company for position listing."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    logo_url: Optional[str] = None
    is_verified: bool


class PositionWithCompany(PositionRead):
    """Position with company details."""
    company: CompanySummary
