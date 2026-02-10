"""
Grade model for tracking partial and exam grades.
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database import Base

if TYPE_CHECKING:
    from app.core.models.user import User
    from app.planning.models.group import Group


class GradeType(str, Enum):
    """Type of grade evaluation."""
    EXAM = "EXAM"
    QUIZ = "QUIZ"
    PARTIAL = "PARTIAL"
    PROJECT = "PROJECT"
    HOMEWORK = "HOMEWORK"
    PARTICIPATION = "PARTICIPATION"
    FINAL = "FINAL"


class PartialGrade(Base):
    """Partial grade for a student in a course."""

    __tablename__ = "partial_grades"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    grade_type: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "Parcial 1", "Quiz 3"
    grade: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    max_grade: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=10.0)
    weight: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=1.0)  # Percentage weight
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    graded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    recorded_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    student: Mapped["User"] = relationship("User", foreign_keys=[student_id])
    group: Mapped["Group"] = relationship("Group")
    recorder: Mapped[Optional["User"]] = relationship("User", foreign_keys=[recorded_by])

    @property
    def normalized_grade(self) -> float:
        """Get grade normalized to 0-10 scale."""
        if self.max_grade == 0:
            return 0.0
        return float(self.grade / self.max_grade * 10)

    @property
    def is_passing(self) -> bool:
        """Check if grade is passing (>=6 on 10 scale)."""
        return self.normalized_grade >= 6.0

    def __repr__(self) -> str:
        return f"<PartialGrade(student={self.student_id}, name={self.name}, grade={self.grade})>"
