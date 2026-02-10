"""Pydantic schemas for AcademicPeriod."""
from datetime import date

from pydantic import BaseModel, Field, ConfigDict, model_validator


class AcademicPeriodBase(BaseModel):
    """Base schema for AcademicPeriod."""
    code: str = Field(..., min_length=3, max_length=20)
    name: str = Field(..., min_length=3, max_length=100)
    start_date: date
    end_date: date
    enrollment_start: date | None = None
    enrollment_end: date | None = None

    @model_validator(mode='after')
    def validate_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError('end_date must be after start_date')
        if self.enrollment_start and self.enrollment_end:
            if self.enrollment_end < self.enrollment_start:
                raise ValueError('enrollment_end must be after enrollment_start')
        return self


class AcademicPeriodCreate(AcademicPeriodBase):
    """Schema for creating an AcademicPeriod."""
    is_current: bool = False


class AcademicPeriodRead(AcademicPeriodBase):
    """Schema for reading an AcademicPeriod."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_current: bool
    is_active: bool
    is_enrollment_open: bool
