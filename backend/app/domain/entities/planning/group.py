"""
Group and Schedule domain entities.
Pure domain logic for course groups and class schedules.
"""
from dataclasses import dataclass, field
from datetime import datetime, time
from enum import IntEnum
from typing import List, Optional


class DayOfWeek(IntEnum):
    """Days of the week enumeration."""
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7
    
    @property
    def spanish_name(self) -> str:
        """Get Spanish name for the day."""
        names = {
            1: "Lunes",
            2: "Martes",
            3: "Miércoles",
            4: "Jueves",
            5: "Viernes",
            6: "Sábado",
            7: "Domingo",
        }
        return names.get(self.value, "Desconocido")


class Modality(str):
    """Class modality types."""
    PRESENCIAL = "presencial"
    VIRTUAL = "virtual"
    HYBRID = "hybrid"


@dataclass
class Schedule:
    """
    Schedule value object.
    Represents a class time slot.
    """
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    classroom: Optional[str] = None
    schedule_type: str = "class"  # class, lab, tutorial
    id: Optional[int] = None
    group_id: Optional[int] = None
    
    def __post_init__(self):
        if isinstance(self.day_of_week, int):
            self.day_of_week = DayOfWeek(self.day_of_week)
        
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time")
    
    @property
    def day_name(self) -> str:
        """Get day name in Spanish."""
        return self.day_of_week.spanish_name
    
    @property
    def time_range(self) -> str:
        """Get formatted time range."""
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
    
    @property
    def duration_minutes(self) -> int:
        """Get duration in minutes."""
        start_mins = self.start_time.hour * 60 + self.start_time.minute
        end_mins = self.end_time.hour * 60 + self.end_time.minute
        return end_mins - start_mins
    
    def overlaps_with(self, other: "Schedule") -> bool:
        """Check if this schedule overlaps with another."""
        if self.day_of_week != other.day_of_week:
            return False
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Schedule):
            return False
        return (
            self.day_of_week == other.day_of_week
            and self.start_time == other.start_time
            and self.end_time == other.end_time
        )
    
    def __hash__(self) -> int:
        return hash((self.day_of_week, self.start_time, self.end_time))


@dataclass
class Group:
    """
    Group domain entity.
    
    Represents a course group/section for a specific period.
    """
    subject_id: int
    period_id: int
    group_number: str
    capacity: int = 30
    enrolled_count: int = 0
    classroom: Optional[str] = None
    modality: str = Modality.PRESENCIAL
    professor_id: Optional[int] = None
    professor_name: Optional[str] = None  # Denormalized for convenience
    subject_code: Optional[str] = None  # Denormalized for convenience
    subject_name: Optional[str] = None  # Denormalized for convenience
    is_active: bool = True
    id: Optional[int] = None
    schedules: List[Schedule] = field(default_factory=list)
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.capacity < 1:
            raise ValueError("Capacity must be at least 1")
        if self.enrolled_count < 0:
            raise ValueError("Enrolled count cannot be negative")
        if not self.group_number.strip():
            raise ValueError("Group number cannot be empty")
    
    @property
    def available_spots(self) -> int:
        """Get number of available spots."""
        return max(0, self.capacity - self.enrolled_count)
    
    @property
    def is_full(self) -> bool:
        """Check if group is at capacity."""
        return self.enrolled_count >= self.capacity
    
    @property
    def display_name(self) -> str:
        """Get display name for the group."""
        if self.subject_code:
            return f"{self.subject_code}-{self.group_number}"
        return f"Group {self.group_number}"
    
    @property
    def occupancy_percentage(self) -> float:
        """Get occupancy as percentage."""
        if self.capacity == 0:
            return 100.0
        return (self.enrolled_count / self.capacity) * 100
    
    def can_enroll(self) -> bool:
        """Check if a student can enroll in this group."""
        return self.is_active and not self.is_full
    
    def increment_enrollment(self) -> None:
        """Increment enrollment count."""
        if self.is_full:
            raise ValueError("Group is already full")
        self.enrolled_count += 1
    
    def decrement_enrollment(self) -> None:
        """Decrement enrollment count."""
        if self.enrolled_count <= 0:
            raise ValueError("Enrollment count is already zero")
        self.enrolled_count -= 1
    
    def add_schedule(self, schedule: Schedule) -> None:
        """Add a schedule to this group."""
        # Check for conflicts with existing schedules
        for existing in self.schedules:
            if schedule.overlaps_with(existing):
                raise ValueError(
                    f"Schedule conflict: {schedule.day_name} {schedule.time_range} "
                    f"overlaps with {existing.day_name} {existing.time_range}"
                )
        self.schedules.append(schedule)
    
    def remove_schedule(self, schedule_id: int) -> bool:
        """Remove a schedule by ID."""
        for i, sched in enumerate(self.schedules):
            if sched.id == schedule_id:
                self.schedules.pop(i)
                return True
        return False
    
    def has_schedule_conflict_with(self, other_schedules: List[Schedule]) -> bool:
        """Check if this group's schedules conflict with given schedules."""
        for my_schedule in self.schedules:
            for other in other_schedules:
                if my_schedule.overlaps_with(other):
                    return True
        return False
    
    def deactivate(self) -> None:
        """Deactivate this group."""
        if not self.is_active:
            raise ValueError("Group is already inactive")
        self.is_active = False
    
    def activate(self) -> None:
        """Activate this group."""
        self.is_active = True
    
    def update_capacity(self, new_capacity: int) -> None:
        """Update group capacity."""
        if new_capacity < 1:
            raise ValueError("Capacity must be at least 1")
        if new_capacity < self.enrolled_count:
            raise ValueError(
                f"Cannot reduce capacity below current enrollment ({self.enrolled_count})"
            )
        self.capacity = new_capacity
    
    def __repr__(self) -> str:
        return f"Group(id={self.id}, subject_id={self.subject_id}, number={self.group_number})"
