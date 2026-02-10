"""
Enrollment domain entity.
Pure domain logic for student course enrollments.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from app.domain.value_objects.planning import Grade


class EnrollmentStatus(str, Enum):
    """Enrollment status enumeration."""
    ENROLLED = "ENROLLED"      # Currently enrolled
    PASSED = "PASSED"          # Completed and passed
    FAILED = "FAILED"          # Completed but failed
    DROPPED = "DROPPED"        # Dropped during semester
    WITHDRAWN = "WITHDRAWN"    # Withdrawn (NP)
    PENDING = "PENDING"        # Pending approval


@dataclass
class Enrollment:
    """
    Enrollment domain entity.
    
    Represents a student's enrollment in a course group.
    """
    student_id: int
    group_id: int
    status: EnrollmentStatus = EnrollmentStatus.ENROLLED
    grade: Optional[Grade] = None
    attempt_number: int = 1
    id: Optional[int] = None
    enrolled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Denormalized fields for convenience
    subject_id: Optional[int] = None
    subject_code: Optional[str] = None
    subject_name: Optional[str] = None
    period_code: Optional[str] = None
    group_number: Optional[str] = None
    credits: Optional[int] = None
    
    def __post_init__(self):
        if isinstance(self.status, str):
            self.status = EnrollmentStatus(self.status)
        if self.attempt_number < 1:
            raise ValueError("Attempt number must be at least 1")
    
    @property
    def grade_value(self) -> Optional[Decimal]:
        """Get grade as Decimal."""
        return self.grade.value if self.grade else None
    
    @property
    def grade_letter(self) -> Optional[str]:
        """Get letter grade."""
        return self.grade.letter if self.grade else None
    
    @property
    def is_completed(self) -> bool:
        """Check if enrollment is completed (passed or failed)."""
        return self.status in (EnrollmentStatus.PASSED, EnrollmentStatus.FAILED)
    
    @property
    def is_active(self) -> bool:
        """Check if enrollment is currently active."""
        return self.status == EnrollmentStatus.ENROLLED
    
    @property
    def was_approved(self) -> bool:
        """Check if student passed the course."""
        return self.status == EnrollmentStatus.PASSED
    
    @property
    def is_pending(self) -> bool:
        """Check if enrollment is pending approval."""
        return self.status == EnrollmentStatus.PENDING
    
    def set_grade(self, grade: float | Decimal | Grade) -> None:
        """Set the grade for this enrollment."""
        if not self.is_active:
            raise ValueError("Cannot set grade for inactive enrollment")
        
        if isinstance(grade, Grade):
            self.grade = grade
        else:
            self.grade = Grade(Decimal(str(grade)))
    
    def complete(self, final_grade: float | Decimal | Grade) -> None:
        """
        Complete the enrollment with a final grade.
        Sets status to PASSED or FAILED based on grade.
        """
        if not self.is_active:
            raise ValueError("Cannot complete inactive enrollment")
        
        self.set_grade(final_grade)
        
        if self.grade.is_passing:
            self.status = EnrollmentStatus.PASSED
        else:
            self.status = EnrollmentStatus.FAILED
        
        self.completed_at = datetime.now()
    
    def drop(self) -> None:
        """Drop the enrollment (during semester)."""
        if not self.is_active:
            raise ValueError("Cannot drop inactive enrollment")
        self.status = EnrollmentStatus.DROPPED
        self.completed_at = datetime.now()
    
    def withdraw(self) -> None:
        """Withdraw from the enrollment (NP)."""
        if not self.is_active:
            raise ValueError("Cannot withdraw from inactive enrollment")
        self.status = EnrollmentStatus.WITHDRAWN
        self.completed_at = datetime.now()
    
    def approve_pending(self) -> None:
        """Approve a pending enrollment."""
        if self.status != EnrollmentStatus.PENDING:
            raise ValueError("Only pending enrollments can be approved")
        self.status = EnrollmentStatus.ENROLLED
        self.enrolled_at = datetime.now()
    
    def reject_pending(self) -> None:
        """Reject a pending enrollment."""
        if self.status != EnrollmentStatus.PENDING:
            raise ValueError("Only pending enrollments can be rejected")
        self.status = EnrollmentStatus.DROPPED
        self.completed_at = datetime.now()
    
    @classmethod
    def create(
        cls,
        student_id: int,
        group_id: int,
        attempt_number: int = 1,
        requires_approval: bool = False,
    ) -> "Enrollment":
        """Factory method to create a new enrollment."""
        return cls(
            student_id=student_id,
            group_id=group_id,
            status=EnrollmentStatus.PENDING if requires_approval else EnrollmentStatus.ENROLLED,
            attempt_number=attempt_number,
            enrolled_at=None if requires_approval else datetime.now(),
        )
    
    def __repr__(self) -> str:
        return f"Enrollment(student={self.student_id}, group={self.group_id}, status={self.status.value})"
