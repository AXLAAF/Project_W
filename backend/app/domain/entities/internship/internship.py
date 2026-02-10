"""
Internship domain entity.
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List

from app.domain.entities.internship.application import InternshipApplication
from app.domain.value_objects.internship import InternshipStatus, InternshipDuration


@dataclass
class Internship:
    """Represents an active internship record."""
    application_id: int
    start_date: date
    expected_end_date: date
    supervisor_name: str
    supervisor_email: str
    supervisor_phone: Optional[str] = None
    status: InternshipStatus = InternshipStatus.ACTIVE
    actual_end_date: Optional[date] = None
    total_hours: int = 0
    final_grade: Optional[float] = None
    completion_certificate_path: Optional[str] = None
    application: Optional[InternshipApplication] = None
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def duration(self) -> InternshipDuration:
        """Get the expected duration."""
        return InternshipDuration(self.start_date, self.expected_end_date)

    def complete(self, end_date: date, final_grade: float, certificate_path: str) -> None:
        """Mark internship as completed."""
        self.status = InternshipStatus.COMPLETED
        self.actual_end_date = end_date
        self.final_grade = final_grade
        self.completion_certificate_path = certificate_path

    def cancel(self) -> None:
        """Cancel the internship."""
        self.status = InternshipStatus.CANCELLED
        self.actual_end_date = date.today()

    def add_hours(self, hours: int) -> None:
        """Add completed hours."""
        if hours < 0:
            raise ValueError("Hours cannot be negative")
        self.total_hours += hours
