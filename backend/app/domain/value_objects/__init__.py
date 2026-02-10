"""Domain value objects package."""
from app.domain.value_objects.email import Email
from app.domain.value_objects.subject_code import SubjectCode
from app.domain.value_objects.credits import Credits
from app.domain.value_objects.grade import Grade

__all__ = ["Email", "SubjectCode", "Credits", "Grade"]
