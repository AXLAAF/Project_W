"""
Enrollment model for student course registrations.
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database import Base

if TYPE_CHECKING:
    from app.core.models.user import User
    from app.planning.models.group import Group


class EnrollmentStatus(str, Enum):
    """Status of an enrollment."""
    ENROLLED = "ENROLLED"      # Currently enrolled
    PASSED = "PASSED"          # Completed and passed
    FAILED = "FAILED"          # Completed but failed
    DROPPED = "DROPPED"        # Dropped during semester
    WITHDRAWN = "WITHDRAWN"    # Withdrawn (NP)
    PENDING = "PENDING"        # Pending approval


class Enrollment(Base):
    """Student enrollment in a course group."""

    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("student_id", "group_id", name="uq_student_group"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default=EnrollmentStatus.ENROLLED.value, nullable=False
    )
    grade: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)
    grade_letter: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    attempt_number: Mapped[int] = mapped_column(default=1)
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    student: Mapped["User"] = relationship("User", foreign_keys=[student_id])
    group: Mapped["Group"] = relationship("Group", back_populates="enrollments")

    @property
    def is_completed(self) -> bool:
        return self.status in (EnrollmentStatus.PASSED.value, EnrollmentStatus.FAILED.value)

    @property
    def is_active(self) -> bool:
        return self.status == EnrollmentStatus.ENROLLED.value

    @property
    def was_approved(self) -> bool:
        return self.status == EnrollmentStatus.PASSED.value

    def calculate_grade_letter(self) -> str | None:
        """Calculate letter grade from numeric grade."""
        if self.grade is None:
            return None
        grade = float(self.grade)
        if grade >= 9.0:
            return "A"
        elif grade >= 8.0:
            return "B"
        elif grade >= 7.0:
            return "C"
        elif grade >= 6.0:
            return "D"
        else:
            return "F"

    def __repr__(self) -> str:
        return f"<Enrollment(student={self.student_id}, group={self.group_id}, status={self.status})>"
