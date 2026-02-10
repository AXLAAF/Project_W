"""
User and Profile Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ============== Profile Schemas ==============

class ProfileBase(BaseModel):
    """Base profile schema with common fields."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    student_id: Optional[str] = Field(None, max_length=50)
    employee_id: Optional[str] = Field(None, max_length=50)
    department: Optional[str] = Field(None, max_length=100)
    program: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)


class ProfileCreate(ProfileBase):
    """Schema for creating a profile."""
    pass


class ProfileUpdate(BaseModel):
    """Schema for updating a profile (all fields optional)."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    program: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    photo_url: Optional[str] = Field(None, max_length=500)


class ProfileRead(ProfileBase):
    """Schema for reading a profile."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    photo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


# ============== User Schemas ==============

class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, max_length=128)
    profile: ProfileCreate


class UserUpdate(BaseModel):
    """Schema for updating a user (admin only)."""
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserRead(UserBase):
    """Schema for reading a user."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    profile: Optional[ProfileRead] = None
    roles: List[str] = []


class UserWithRoles(UserRead):
    """User with expanded role information."""
    pass
