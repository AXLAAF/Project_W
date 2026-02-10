"""
Attendance model for tracking student class attendance.
"""
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database import Base

if TYPE_CHECKING:
    from app.core.models.user import User
    from app.planning.models.group import Group


class Attendance(Base):
    """Student attendance record for a class session."""

    __tablename__ = "attendances"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    class_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # PRESENT, ABSENT, LATE, EXCUSED
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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
    def is_present(self) -> bool:
        return self.status in ("PRESENT", "LATE")

    @property
    def is_absence(self) -> bool:
        return self.status in ("ABSENT",)

    def __repr__(self) -> str:
        return f"<Attendance(student={self.student_id}, date={self.class_date}, status={self.status})>"
