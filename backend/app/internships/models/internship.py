"""
Internship model for active internship records.
"""
import enum
from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database import Base

if TYPE_CHECKING:
    from app.internships.models.internship_application import InternshipApplication
    from app.internships.models.internship_report import InternshipReport


class InternshipStatus(str, enum.Enum):
    """Internship status options."""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class Internship(Base):
    """Active internship record after application approval."""

    __tablename__ = "internships"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("internship_applications.id", ondelete="CASCADE"), 
        unique=True, nullable=False
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[InternshipStatus] = mapped_column(
        Enum(InternshipStatus), default=InternshipStatus.ACTIVE, nullable=False
    )
    supervisor_name: Mapped[str] = mapped_column(String(200), nullable=False)
    supervisor_email: Mapped[str] = mapped_column(String(255), nullable=False)
    supervisor_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    total_hours: Mapped[int] = mapped_column(default=0, nullable=False)
    final_grade: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    completion_certificate_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    application: Mapped["InternshipApplication"] = relationship(
        "InternshipApplication", back_populates="internship"
    )
    reports: Mapped[List["InternshipReport"]] = relationship(
        "InternshipReport", back_populates="internship", cascade="all, delete-orphan"
    )

    @property
    def is_active(self) -> bool:
        """Check if internship is currently active."""
        return self.status == InternshipStatus.ACTIVE

    def __repr__(self) -> str:
        return f"<Internship(id={self.id}, application_id={self.application_id}, status={self.status})>"
