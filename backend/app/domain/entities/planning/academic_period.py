"""
AcademicPeriod domain entity.
Pure domain logic for academic periods (semesters, trimesters, etc.).
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from app.domain.value_objects.planning import PeriodCode


@dataclass
class AcademicPeriod:
    """
    AcademicPeriod domain entity.
    
    Represents an academic period (semester, trimester, etc.).
    """
    code: PeriodCode
    name: str
    start_date: date
    end_date: date
    enrollment_start: Optional[date] = None
    enrollment_end: Optional[date] = None
    is_current: bool = False
    is_active: bool = True
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if isinstance(self.code, str):
            self.code = PeriodCode(self.code)
        
        if self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")
        
        if self.enrollment_start and self.enrollment_end:
            if self.enrollment_start > self.enrollment_end:
                raise ValueError("Enrollment start must be before enrollment end")
    
    @property
    def code_str(self) -> str:
        """Get code as string."""
        return str(self.code)
    
    @property
    def year(self) -> int:
        """Get year from period code."""
        return self.code.year
    
    @property
    def period_number(self) -> int:
        """Get period number from code."""
        return self.code.period_number
    
    @property
    def is_enrollment_open(self) -> bool:
        """Check if enrollment is currently open."""
        if not self.enrollment_start or not self.enrollment_end:
            return False
        today = date.today()
        return self.enrollment_start <= today <= self.enrollment_end
    
    @property
    def is_in_progress(self) -> bool:
        """Check if period is currently in progress."""
        today = date.today()
        return self.start_date <= today <= self.end_date
    
    @property
    def is_finished(self) -> bool:
        """Check if period has finished."""
        return date.today() > self.end_date
    
    @property
    def is_upcoming(self) -> bool:
        """Check if period has not started yet."""
        return date.today() < self.start_date
    
    @property
    def duration_days(self) -> int:
        """Get duration of period in days."""
        return (self.end_date - self.start_date).days
    
    @property
    def days_remaining(self) -> Optional[int]:
        """Get remaining days if period is in progress."""
        if not self.is_in_progress:
            return None
        return (self.end_date - date.today()).days
    
    @property
    def enrollment_days_remaining(self) -> Optional[int]:
        """Get remaining enrollment days."""
        if not self.is_enrollment_open:
            return None
        return (self.enrollment_end - date.today()).days
    
    def set_as_current(self) -> None:
        """Mark this period as the current period."""
        self.is_current = True
    
    def unset_as_current(self) -> None:
        """Unmark this period as current."""
        self.is_current = False
    
    def deactivate(self) -> None:
        """Deactivate this period."""
        if not self.is_active:
            raise ValueError("Period is already inactive")
        self.is_active = False
    
    def activate(self) -> None:
        """Activate this period."""
        self.is_active = True
    
    def update_enrollment_dates(
        self,
        enrollment_start: Optional[date] = None,
        enrollment_end: Optional[date] = None,
    ) -> None:
        """Update enrollment dates."""
        if enrollment_start is not None:
            self.enrollment_start = enrollment_start
        if enrollment_end is not None:
            self.enrollment_end = enrollment_end
        
        if self.enrollment_start and self.enrollment_end:
            if self.enrollment_start > self.enrollment_end:
                raise ValueError("Enrollment start must be before enrollment end")
    
    @classmethod
    def create(
        cls,
        code: str,
        name: str,
        start_date: date,
        end_date: date,
        enrollment_start: Optional[date] = None,
        enrollment_end: Optional[date] = None,
    ) -> "AcademicPeriod":
        """Factory method to create a new academic period."""
        if not name.strip():
            raise ValueError("Period name cannot be empty")
        
        return cls(
            code=PeriodCode(code),
            name=name.strip(),
            start_date=start_date,
            end_date=end_date,
            enrollment_start=enrollment_start,
            enrollment_end=enrollment_end,
            is_current=False,
            is_active=True,
        )
    
    def __repr__(self) -> str:
        return f"AcademicPeriod(code={self.code}, name={self.name})"
