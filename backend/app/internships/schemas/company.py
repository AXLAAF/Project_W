"""
Company Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict, HttpUrl


class CompanyBase(BaseModel):
    """Base company schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    rfc: str = Field(..., min_length=12, max_length=13, pattern=r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$")
    contact_email: EmailStr
    contact_phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    website: Optional[str] = Field(None, max_length=255)


class CompanyCreate(CompanyBase):
    """Schema for creating a company."""
    pass


class CompanyUpdate(BaseModel):
    """Schema for updating a company (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    website: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=500)


class CompanyVerify(BaseModel):
    """Schema for verifying a company (admin only)."""
    is_verified: bool


class CompanyRead(CompanyBase):
    """Schema for reading a company."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    logo_url: Optional[str] = None
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CompanyList(BaseModel):
    """Schema for listing companies with pagination."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    rfc: str
    contact_email: str
    is_verified: bool
    is_active: bool
