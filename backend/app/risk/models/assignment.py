"""
Assignment and Submission models for tracking homework deliveries.
"""
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database import Base

if TYPE_CHECKING:
    from app.core.models.user import User
    from app.planning.models.group import Group


class SubmissionStatus(str, Enum):
    """Status of an assignment submission."""
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    LATE = "LATE"
    GRADED = "GRADED"
    MISSING = "MISSING"


class Assignment(Base):
    """Assignment/homework definition for a group."""

    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    max_score: Mapped[float] = mapped_column(default=100.0)
    weight: Mapped[float] = mapped_column(default=1.0)
    allows_late: Mapped[bool] = mapped_column(Boolean, default=True)
    late_penalty_percent: Mapped[float] = mapped_column(default=10.0)  # % per day
    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    group: Mapped["Group"] = relationship("Group")
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by])
    submissions: Mapped[list["AssignmentSubmission"]] = relationship(
        "AssignmentSubmission", back_populates="assignment", cascade="all, delete-orphan"
    )

    @property
    def is_past_due(self) -> bool:
        return datetime.now(self.due_date.tzinfo) > self.due_date

    def __repr__(self) -> str:
        return f"<Assignment(id={self.id}, title={self.title})>"


class AssignmentSubmission(Base):
    """Student submission for an assignment."""

    __tablename__ = "assignment_submissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    assignment_id: Mapped[int] = mapped_column(
        ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default=SubmissionStatus.PENDING.value, nullable=False
    )
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    score: Mapped[float | None] = mapped_column(nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    graded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    graded_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    assignment: Mapped["Assignment"] = relationship("Assignment", back_populates="submissions")
    student: Mapped["User"] = relationship("User", foreign_keys=[student_id])
    grader: Mapped[Optional["User"]] = relationship("User", foreign_keys=[graded_by])

    @property
    def is_late(self) -> bool:
        if self.submitted_at and self.assignment:
            return self.submitted_at > self.assignment.due_date
        return False

    @property
    def days_late(self) -> int:
        if not self.is_late or not self.submitted_at:
            return 0
        delta = self.submitted_at - self.assignment.due_date
        return max(0, delta.days)

    def __repr__(self) -> str:
        return f"<AssignmentSubmission(assignment={self.assignment_id}, student={self.student_id})>"
