"""
Academic Period model.
"""
from datetime import date, datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, Date, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database import Base

if TYPE_CHECKING:
    from app.planning.models.group import Group


class AcademicPeriod(Base):
    """Academic period (semester, trimester, etc.)."""

    __tablename__ = "academic_periods"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)  # e.g., "2026-1"
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "Primavera 2026"
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    enrollment_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    enrollment_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    groups: Mapped[List["Group"]] = relationship(
        "Group", back_populates="period", cascade="all, delete-orphan"
    )

    @property
    def is_enrollment_open(self) -> bool:
        """Check if enrollment is currently open."""
        if not self.enrollment_start or not self.enrollment_end:
            return False
        today = date.today()
        return self.enrollment_start <= today <= self.enrollment_end

    def __repr__(self) -> str:
        return f"<AcademicPeriod(code={self.code}, name={self.name})>"
