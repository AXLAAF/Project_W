"""
InternshipReport model for monthly progress reports.
"""
import enum
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database import Base

if TYPE_CHECKING:
    from app.internships.models.internship import Internship


class ReportStatus(str, enum.Enum):
    """Report status options."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REVISION_NEEDED = "revision_needed"


class InternshipReport(Base):
    """Monthly progress report for an active internship."""

    __tablename__ = "internship_reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    internship_id: Mapped[int] = mapped_column(
        ForeignKey("internships.id", ondelete="CASCADE"), nullable=False, index=True
    )
    month_number: Mapped[int] = mapped_column(Integer, nullable=False)
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    hours_worked: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    activities_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    achievements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    challenges: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    supervisor_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    supervisor_grade: Mapped[Optional[float]] = mapped_column(nullable=True)
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus), default=ReportStatus.DRAFT, nullable=False
    )
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    internship: Mapped["Internship"] = relationship("Internship", back_populates="reports")

    def __repr__(self) -> str:
        return f"<InternshipReport(id={self.id}, internship_id={self.internship_id}, month={self.month_number})>"
