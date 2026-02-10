"""
InternshipApplication domain entity.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.domain.entities.internship.position import InternshipPosition
from app.domain.value_objects.internship import ApplicationStatus


@dataclass
class InternshipApplication:
    """Represents a student's application for an internship position."""
    student_id: int
    position_id: int
    cv_url: Optional[str] = None
    cover_letter: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.PENDING
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    comments: Optional[str] = None
    position: Optional[InternshipPosition] = None
    id: Optional[int] = None
    submitted_at: datetime = field(default_factory=datetime.now)

    def approve(self, reviewer_id: int, comments: Optional[str] = None) -> None:
        """Approve the application."""
        self.status = ApplicationStatus.APPROVED
        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.now()
        self.comments = comments

    def reject(self, reviewer_id: int, comments: Optional[str] = None) -> None:
        """Reject the application."""
        self.status = ApplicationStatus.REJECTED
        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.now()
        self.comments = comments

    @property
    def is_pending(self) -> bool:
        return self.status == ApplicationStatus.PENDING
