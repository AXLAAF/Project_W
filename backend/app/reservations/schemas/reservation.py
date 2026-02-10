"""Pydantic schemas for Reservation."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.reservations.models import ReservationStatus


class ReservationBase(BaseModel):
    """Base schema for Reservation."""
    resource_id: int
    start_time: datetime
    end_time: datetime
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    attendees_count: Optional[int] = Field(None, ge=1)
    
    @field_validator('end_time')
    @classmethod
    def end_after_start(cls, v: datetime, info) -> datetime:
        start = info.data.get('start_time')
        if start and v <= start:
            raise ValueError('end_time must be after start_time')
        return v


class ReservationCreate(ReservationBase):
    """Schema for creating a Reservation."""
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None


class ReservationUpdate(BaseModel):
    """Schema for updating a Reservation."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    attendees_count: Optional[int] = Field(None, ge=1)


class ReservationApprove(BaseModel):
    """Schema for approving a reservation."""
    pass


class ReservationReject(BaseModel):
    """Schema for rejecting a reservation."""
    rejection_reason: str = Field(..., min_length=10, max_length=500)


class ReservationCheckIn(BaseModel):
    """Schema for checking in to a reservation."""
    pass


class ReservationCheckOut(BaseModel):
    """Schema for checking out of a reservation."""
    pass


class ResourceSummary(BaseModel):
    """Summary of resource for reservation display."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    code: str
    location: Optional[str] = None


class ReservationRead(BaseModel):
    """Schema for reading a Reservation."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    resource_id: int
    user_id: int
    start_time: datetime
    end_time: datetime
    title: str
    description: Optional[str] = None
    attendees_count: Optional[int] = None
    status: ReservationStatus
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    checked_in_at: Optional[datetime] = None
    checked_out_at: Optional[datetime] = None
    is_recurring: bool
    created_at: datetime
    updated_at: datetime


class ReservationWithResource(ReservationRead):
    """Reservation with resource details."""
    resource: Optional[ResourceSummary] = None


class ReservationCalendarItem(BaseModel):
    """Simplified reservation for calendar display."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    resource_id: int
    start_time: datetime
    end_time: datetime
    title: str
    status: ReservationStatus
