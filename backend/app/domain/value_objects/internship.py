"""
Internship domain value objects.
"""
from enum import Enum, unique
from dataclasses import dataclass
from datetime import date, timedelta


@unique
class ApplicationStatus(str, Enum):
    """Status of an internship application."""
    PENDING = "PENDING"
    REVIEWING = "REVIEWING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


@unique
class InternshipStatus(str, Enum):
    """Status of an active internship."""
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ON_HOLD = "ON_HOLD"


@unique
class ReportType(str, Enum):
    """Type of internship report."""
    PARTIAL = "PARTIAL"
    FINAL = "FINAL"


@unique
class ReportStatus(str, Enum):
    """Status of an internship report."""
    PENDING = "PENDING"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@unique
class CompanyStatus(str, Enum):
    """Status of a company partner."""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BLACKLISTED = "BLACKLISTED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"


@dataclass(frozen=True)
class InternshipDuration:
    """Value object representing internship duration."""
    start_date: date
    end_date: date

    def __post_init__(self):
        if self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")

    @property
    def weeks(self) -> int:
        """Calculate duration in weeks."""
        return (self.end_date - self.start_date).days // 7
    
    @property
    def days(self) -> int:
        """Calculate duration in days."""
        return (self.end_date - self.start_date).days
