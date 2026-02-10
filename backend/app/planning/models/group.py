"""
Group and Schedule models.
"""
from datetime import datetime, time
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, SmallInteger, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database import Base

if TYPE_CHECKING:
    from app.planning.models.subject import Subject
    from app.planning.models.academic_period import AcademicPeriod
    from app.planning.models.enrollment import Enrollment
    from app.core.models.user import User


class DayOfWeek(int, Enum):
    """Days of the week."""
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class Group(Base):
    """Course group/section for a specific period."""

    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    period_id: Mapped[int] = mapped_column(
        ForeignKey("academic_periods.id", ondelete="CASCADE"), nullable=False, index=True
    )
    professor_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    group_number: Mapped[str] = mapped_column(String(10), nullable=False)  # e.g., "001", "A"
    capacity: Mapped[int] = mapped_column(Integer, default=30)
    enrolled_count: Mapped[int] = mapped_column(Integer, default=0)
    classroom: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    modality: Mapped[str] = mapped_column(String(20), default="presencial")  # presencial, virtual, hybrid
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    subject: Mapped["Subject"] = relationship("Subject", back_populates="groups")
    period: Mapped["AcademicPeriod"] = relationship("AcademicPeriod", back_populates="groups")
    professor: Mapped[Optional["User"]] = relationship("User", foreign_keys=[professor_id])
    schedules: Mapped[List["Schedule"]] = relationship(
        "Schedule", back_populates="group", cascade="all, delete-orphan"
    )
    enrollments: Mapped[List["Enrollment"]] = relationship(
        "Enrollment", back_populates="group", cascade="all, delete-orphan"
    )

    @property
    def available_spots(self) -> int:
        return max(0, self.capacity - self.enrolled_count)

    @property
    def is_full(self) -> bool:
        return self.enrolled_count >= self.capacity

    @property
    def display_name(self) -> str:
        return f"{self.subject.code}-{self.group_number}"

    def __repr__(self) -> str:
        return f"<Group(id={self.id}, subject_id={self.subject_id}, number={self.group_number})>"


class Schedule(Base):
    """Class schedule for a group."""

    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    day_of_week: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 1-7 (Mon-Sun)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    classroom: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    schedule_type: Mapped[str] = mapped_column(String(20), default="class")  # class, lab, tutorial

    # Relationships
    group: Mapped["Group"] = relationship("Group", back_populates="schedules")

    @property
    def day_name(self) -> str:
        days = ["", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        return days[self.day_of_week] if 1 <= self.day_of_week <= 7 else "Unknown"

    @property
    def time_range(self) -> str:
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

    def overlaps_with(self, other: "Schedule") -> bool:
        """Check if this schedule overlaps with another."""
        if self.day_of_week != other.day_of_week:
            return False
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)

    def __repr__(self) -> str:
        return f"<Schedule(group_id={self.group_id}, day={self.day_name}, time={self.time_range})>"
