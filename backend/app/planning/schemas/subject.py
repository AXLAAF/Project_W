"""Pydantic schemas for Subject."""
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class SubjectBase(BaseModel):
    """Base schema for Subject."""
    code: str = Field(..., min_length=2, max_length=20)
    name: str = Field(..., min_length=3, max_length=200)
    credits: int = Field(..., ge=1, le=20)
    hours_theory: int = Field(default=0, ge=0)
    hours_practice: int = Field(default=0, ge=0)
    hours_lab: int = Field(default=0, ge=0)
    description: Optional[str] = None
    department: Optional[str] = Field(default=None, max_length=100)
    semester_suggested: Optional[int] = Field(default=None, ge=1, le=15)


class SubjectCreate(SubjectBase):
    """Schema for creating a Subject."""
    prerequisite_ids: List[int] = Field(default_factory=list)


class SubjectUpdate(BaseModel):
    """Schema for updating a Subject."""
    name: Optional[str] = Field(default=None, min_length=3, max_length=200)
    credits: Optional[int] = Field(default=None, ge=1, le=20)
    hours_theory: Optional[int] = Field(default=None, ge=0)
    hours_practice: Optional[int] = Field(default=None, ge=0)
    hours_lab: Optional[int] = Field(default=None, ge=0)
    description: Optional[str] = None
    department: Optional[str] = None
    semester_suggested: Optional[int] = Field(default=None, ge=1, le=15)
    is_active: Optional[bool] = None


class SubjectRead(SubjectBase):
    """Schema for reading a Subject."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    total_hours: int


class PrerequisiteRead(BaseModel):
    """Schema for reading a prerequisite reference."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    credits: int


class SubjectWithPrerequisites(SubjectRead):
    """Schema for Subject with prerequisites."""
    prerequisites: List[PrerequisiteRead] = Field(default_factory=list)
    required_by: List[PrerequisiteRead] = Field(default_factory=list)


class PrerequisiteCreate(BaseModel):
    """Schema for adding a prerequisite."""
    prerequisite_id: int
    is_mandatory: bool = True
