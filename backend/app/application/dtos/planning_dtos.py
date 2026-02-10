from dataclasses import dataclass, field
from datetime import datetime
import datetime as dt
from typing import List, Optional

@dataclass
class PrerequisiteDTO:
    id: int
    code: str
    name: str
    credits: int
    is_mandatory: bool

@dataclass
class SubjectDTO:
    id: int
    code: str
    name: str
    credits: int
    hours_theory: int
    hours_practice: int
    hours_lab: int
    total_hours: int
    description: Optional[str] = None
    department: Optional[str] = None
    semester_suggested: Optional[int] = None
    is_active: bool = True
    prerequisites: List[PrerequisiteDTO] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class CreateSubjectDTO:
    code: str
    name: str
    credits: int
    hours_theory: int = 0
    hours_practice: int = 0
    hours_lab: int = 0
    description: Optional[str] = None
    department: Optional[str] = None
    semester_suggested: Optional[int] = None
    prerequisite_ids: List[int] = field(default_factory=list)

@dataclass
class UpdateSubjectDTO:
    name: Optional[str] = None
    credits: Optional[int] = None
    hours_theory: Optional[int] = None
    hours_practice: Optional[int] = None
    hours_lab: Optional[int] = None
    description: Optional[str] = None
    department: Optional[str] = None
    semester_suggested: Optional[int] = None
    is_active: Optional[bool] = None

@dataclass
class ScheduleDTO:
    id: int
    group_id: int
    day_of_week: int
    start_time: datetime.time
    end_time: datetime.time
    classroom: Optional[str]
    schedule_type: str
    day_name: str = ""
    time_range: str = ""

@dataclass
class GroupDTO:
    id: int
    code: str
    subject_id: int
    academic_period_id: int
    teacher_id: Optional[int] = None
    quota: int = 0
    enrolled_count: int = 0
    available_spots: int = 0
    is_full: bool = False
    schedule_summary: Optional[str] = None
    is_active: bool = True
    subject_code: str = ""
    subject_name: str = ""
    teacher_name: Optional[str] = None
    schedules: List[ScheduleDTO] = field(default_factory=list)


@dataclass
class CreateGroupDTO:
    subject_id: int
    academic_period_id: int
    code: str
    teacher_id: Optional[int] = None
    quota: int = 30
    schedule_summary: Optional[str] = None

@dataclass
class EnrollmentDTO:
    id: int
    student_id: int
    group_id: int
    status: str
    grade: Optional[float] = None
    enrolled_at: datetime = field(default_factory=datetime.now)
    subject_code: str = ""
    subject_name: str = ""
    group_code: str = ""
