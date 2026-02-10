"""
InternshipReport domain entity.
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional

from app.domain.value_objects.internship import ReportType, ReportStatus


@dataclass
class InternshipReport:
    """Represents a progress report submitted during an internship."""
    internship_id: int
    report_type: ReportType
    start_date: date
    end_date: date
    content: str
    hours_logged: int = 0
    status: ReportStatus = ReportStatus.PENDING
    file_url: Optional[str] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    comments: Optional[str] = None
    id: Optional[int] = None
    submitted_at: datetime = field(default_factory=datetime.now)

    def approve(self, reviewer_id: int, comments: Optional[str] = None) -> None:
        """Approve the report."""
        self.status = ReportStatus.APPROVED
        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.now()
        self.comments = comments

    def reject(self, reviewer_id: int, comments: Optional[str] = None) -> None:
        """Reject the report."""
        self.status = ReportStatus.REJECTED
        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.now()
        self.comments = comments
