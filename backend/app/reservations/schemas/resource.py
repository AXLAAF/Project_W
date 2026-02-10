"""Pydantic schemas for Resource."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.reservations.models import ResourceType, ResourceStatus


class ResourceBase(BaseModel):
    """Base schema for Resource."""
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    resource_type: ResourceType
    location: Optional[str] = Field(None, max_length=200)
    building: Optional[str] = Field(None, max_length=100)
    floor: Optional[str] = Field(None, max_length=20)
    capacity: Optional[int] = Field(None, ge=1)
    features: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)
    min_reservation_minutes: int = Field(30, ge=15, le=480)
    max_reservation_minutes: int = Field(240, ge=30, le=720)
    advance_booking_days: int = Field(14, ge=1, le=90)
    requires_approval: bool = False


class ResourceCreate(ResourceBase):
    """Schema for creating a Resource."""
    responsible_user_id: Optional[int] = None


class ResourceUpdate(BaseModel):
    """Schema for updating a Resource."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    resource_type: Optional[ResourceType] = None
    location: Optional[str] = Field(None, max_length=200)
    building: Optional[str] = Field(None, max_length=100)
    floor: Optional[str] = Field(None, max_length=20)
    capacity: Optional[int] = Field(None, ge=1)
    features: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)
    status: Optional[ResourceStatus] = None
    min_reservation_minutes: Optional[int] = Field(None, ge=15, le=480)
    max_reservation_minutes: Optional[int] = Field(None, ge=30, le=720)
    advance_booking_days: Optional[int] = Field(None, ge=1, le=90)
    requires_approval: Optional[bool] = None
    is_active: Optional[bool] = None
    responsible_user_id: Optional[int] = None


class ResourceRead(ResourceBase):
    """Schema for reading a Resource."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: ResourceStatus
    is_active: bool
    responsible_user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class ResourceList(BaseModel):
    """Simplified schema for listing resources."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    code: str
    resource_type: ResourceType
    location: Optional[str] = None
    capacity: Optional[int] = None
    status: ResourceStatus
    is_active: bool
    image_url: Optional[str] = None
