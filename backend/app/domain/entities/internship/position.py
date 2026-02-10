"""
InternshipPosition domain entity.
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional

from app.domain.entities.internship.company import Company
from app.domain.value_objects.internship import InternshipStatus


@dataclass
class InternshipPosition:
    """Represents an internship vacancy/position offered by a company."""
    company_id: int
    title: str
    description: str
    requirements: str
    location: Optional[str] = None
    is_remote: bool = False
    salary: Optional[float] = None
    application_deadline: Optional[date] = None
    is_active: bool = True
    company: Optional[Company] = None
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    def close(self) -> None:
        """Close the position for new applications."""
        self.is_active = False

    @property
    def is_open(self) -> bool:
        """Check if position is open for applications."""
        if not self.is_active:
            return False
        if self.application_deadline and date.today() > self.application_deadline:
            return False
        return True
