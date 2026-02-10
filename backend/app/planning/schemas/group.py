"""Pydantic schemas for Group and Schedule."""
from datetime import time
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict, model_validator


class ScheduleBase(BaseModel):
    """Base schema for Schedule."""
    day_of_week: int = Field(..., ge=1, le=7)
    start_time: time
    end_time: time
    classroom: Optional[str] = Field(default=None, max_length=50)
    schedule_type: str = Field(default="class", pattern="^(class|lab|tutorial)$")

    @model_validator(mode='after')
    def validate_times(self):
        if self.end_time <= self.start_time:
            raise ValueError('end_time must be after start_time')
        return self


class ScheduleCreate(ScheduleBase):
    """Schema for creating a Schedule."""
    pass


class ScheduleRead(ScheduleBase):
    """Schema for reading a Schedule."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    day_name: str
    time_range: str


class GroupBase(BaseModel):
    """Base schema for Group."""
    group_number: str = Field(..., min_length=1, max_length=10)
    capacity: int = Field(default=30, ge=1, le=500)
    classroom: Optional[str] = Field(default=None, max_length=50)
    modality: str = Field(default="presencial", pattern="^(presencial|virtual|hybrid)$")


class GroupCreate(GroupBase):
    """Schema for creating a Group."""
    subject_id: int
    period_id: int
    professor_id: Optional[int] = None
    schedules: List[ScheduleCreate] = Field(default_factory=list)


class ProfessorInfo(BaseModel):
    """Schema for professor info in Group."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str | None = None
    last_name: str | None = None


class SubjectInfo(BaseModel):
    """Schema for subject info in Group."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    credits: int


class GroupRead(GroupBase):
    """Schema for reading a Group."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject_id: int
    period_id: int
    professor_id: Optional[int] = None
    enrolled_count: int
    available_spots: int
    is_full: bool
    is_active: bool


class GroupWithSchedules(GroupRead):
    """Schema for Group with schedules and related info."""
    schedules: List[ScheduleRead] = Field(default_factory=list)
    subject: SubjectInfo | None = None


class GroupWithDetails(GroupWithSchedules):
    """Schema for Group with all details including professor."""
    professor: ProfessorInfo | None = None
