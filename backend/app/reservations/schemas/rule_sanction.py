"""Pydantic schemas for ReservationRule and UserSanction."""
from datetime import datetime, time
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.reservations.models import RuleType, SanctionType, SanctionReason


# ============ ReservationRule Schemas ============

class RuleBase(BaseModel):
    """Base schema for ReservationRule."""
    resource_id: Optional[int] = None
    rule_type: RuleType
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_reservations_per_day: Optional[int] = Field(None, ge=1)
    max_reservations_per_week: Optional[int] = Field(None, ge=1)
    max_hours_per_day: Optional[int] = Field(None, ge=1)
    max_hours_per_week: Optional[int] = Field(None, ge=1)
    priority: int = 0


class RuleCreate(RuleBase):
    """Schema for creating a ReservationRule."""
    pass


class RuleUpdate(BaseModel):
    """Schema for updating a ReservationRule."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_reservations_per_day: Optional[int] = Field(None, ge=1)
    max_reservations_per_week: Optional[int] = Field(None, ge=1)
    max_hours_per_day: Optional[int] = Field(None, ge=1)
    max_hours_per_week: Optional[int] = Field(None, ge=1)
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class RuleRead(RuleBase):
    """Schema for reading a ReservationRule."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ============ UserSanction Schemas ============

class SanctionBase(BaseModel):
    """Base schema for UserSanction."""
    user_id: int
    reservation_id: Optional[int] = None
    sanction_type: SanctionType
    reason: SanctionReason
    description: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None


class SanctionCreate(SanctionBase):
    """Schema for creating a UserSanction."""
    pass


class SanctionResolve(BaseModel):
    """Schema for resolving a sanction."""
    resolution_notes: Optional[str] = None


class SanctionRead(SanctionBase):
    """Schema for reading a UserSanction."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    applied_by_id: int
    is_resolved: bool
    resolved_at: Optional[datetime] = None
    resolved_by_id: Optional[int] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
