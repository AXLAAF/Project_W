"""Planning module schemas package."""
from app.planning.schemas.subject import (
    SubjectBase,
    SubjectCreate,
    SubjectUpdate,
    SubjectRead,
    SubjectWithPrerequisites,
    PrerequisiteCreate,
)
from app.planning.schemas.period import (
    AcademicPeriodBase,
    AcademicPeriodCreate,
    AcademicPeriodRead,
)
from app.planning.schemas.group import (
    GroupBase,
    GroupCreate,
    GroupRead,
    GroupWithSchedules,
    ScheduleBase,
    ScheduleCreate,
    ScheduleRead,
)
from app.planning.schemas.enrollment import (
    EnrollmentCreate,
    EnrollmentRead,
    EnrollmentUpdate,
    AcademicHistoryItem,
    AcademicHistorySummary,
)

__all__ = [
    "SubjectBase",
    "SubjectCreate",
    "SubjectUpdate",
    "SubjectRead",
    "SubjectWithPrerequisites",
    "PrerequisiteCreate",
    "AcademicPeriodBase",
    "AcademicPeriodCreate",
    "AcademicPeriodRead",
    "GroupBase",
    "GroupCreate",
    "GroupRead",
    "GroupWithSchedules",
    "ScheduleBase",
    "ScheduleCreate",
    "ScheduleRead",
    "EnrollmentCreate",
    "EnrollmentRead",
    "EnrollmentUpdate",
    "AcademicHistoryItem",
    "AcademicHistorySummary",
]
