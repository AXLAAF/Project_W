"""
Attendance domain entity.
Pure domain logic for student class attendance.
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from app.domain.value_objects.risk import AttendanceStatus


@dataclass
class Attendance:
    """
    Attendance domain entity.
    
    Represents a student's attendance record for a class session.
    """
    student_id: int
    group_id: int
    class_date: date
    status: AttendanceStatus
    notes: Optional[str] = None
    recorded_by: Optional[int] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    # Denormalized fields for convenience
    student_name: Optional[str] = None
    subject_code: Optional[str] = None
    
    def __post_init__(self):
        if isinstance(self.status, str):
            self.status = AttendanceStatus(self.status)
        if isinstance(self.class_date, datetime):
            self.class_date = self.class_date.date()
    
    @property
    def is_present(self) -> bool:
        """Check if student was present (includes late)."""
        return self.status.counts_as_present
    
    @property
    def is_absence(self) -> bool:
        """Check if this is an unexcused absence."""
        return self.status.counts_as_absence
    
    @property
    def is_excused(self) -> bool:
        """Check if absence was excused."""
        return self.status == AttendanceStatus.EXCUSED
    
    def mark_as(self, status: AttendanceStatus, recorded_by: int) -> None:
        """Update attendance status."""
        self.status = status
        self.recorded_by = recorded_by
    
    def excuse(self, recorded_by: int, notes: Optional[str] = None) -> None:
        """Mark attendance as excused."""
        if self.status != AttendanceStatus.ABSENT:
            raise ValueError("Can only excuse an absent record")
        self.status = AttendanceStatus.EXCUSED
        self.recorded_by = recorded_by
        if notes:
            self.notes = notes
    
    @classmethod
    def record(
        cls,
        student_id: int,
        group_id: int,
        class_date: date,
        status: AttendanceStatus,
        recorded_by: int,
        notes: Optional[str] = None,
    ) -> "Attendance":
        """Factory method to record attendance."""
        return cls(
            student_id=student_id,
            group_id=group_id,
            class_date=class_date,
            status=status,
            recorded_by=recorded_by,
            notes=notes,
        )
    
    def __repr__(self) -> str:
        return f"Attendance(student={self.student_id}, date={self.class_date}, status={self.status.value})"


@dataclass
class AttendanceStats:
    """Statistics aggregate for attendance calculations."""
    total_classes: int = 0
    present: int = 0
    absent: int = 0
    late: int = 0
    excused: int = 0
    
    @property
    def attendance_rate(self) -> float:
        """Calculate attendance rate as percentage."""
        if self.total_classes == 0:
            return 100.0
        return ((self.present + self.late) / self.total_classes) * 100
    
    @property
    def absence_rate(self) -> float:
        """Calculate absence rate as percentage."""
        if self.total_classes == 0:
            return 0.0
        return (self.absent / self.total_classes) * 100
    
    @classmethod
    def from_records(cls, attendances: list["Attendance"]) -> "AttendanceStats":
        """Create stats from attendance records."""
        stats = cls(total_classes=len(attendances))
        for a in attendances:
            if a.status == AttendanceStatus.PRESENT:
                stats.present += 1
            elif a.status == AttendanceStatus.ABSENT:
                stats.absent += 1
            elif a.status == AttendanceStatus.LATE:
                stats.late += 1
            elif a.status == AttendanceStatus.EXCUSED:
                stats.excused += 1
        return stats
