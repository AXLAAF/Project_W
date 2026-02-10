"""
Enrollment repository interface (port).
Defines the contract for enrollment persistence operations.
"""
from abc import ABC, abstractmethod
from typing import Optional, Sequence, Tuple

from app.domain.entities.planning.enrollment import Enrollment, EnrollmentStatus


class IEnrollmentRepository(ABC):
    """
    Abstract interface for enrollment repository.
    
    This is a 'port' in hexagonal architecture terminology.
    """
    
    @abstractmethod
    async def get_by_id(self, enrollment_id: int) -> Optional[Enrollment]:
        """Get an enrollment by ID."""
        pass
    
    @abstractmethod
    async def save(self, enrollment: Enrollment) -> Enrollment:
        """Save a new enrollment."""
        pass
    
    @abstractmethod
    async def update(self, enrollment: Enrollment) -> Enrollment:
        """Update an existing enrollment."""
        pass
    
    @abstractmethod
    async def delete(self, enrollment_id: int) -> bool:
        """Delete an enrollment."""
        pass
    
    @abstractmethod
    async def get_by_student_and_group(
        self,
        student_id: int,
        group_id: int,
    ) -> Optional[Enrollment]:
        """Get enrollment for a specific student in a specific group."""
        pass
    
    @abstractmethod
    async def list_by_student(
        self,
        student_id: int,
        status: Optional[EnrollmentStatus] = None,
        period_id: Optional[int] = None,
    ) -> Sequence[Enrollment]:
        """Get all enrollments for a student."""
        pass
    
    @abstractmethod
    async def list_by_group(
        self,
        group_id: int,
        status: Optional[EnrollmentStatus] = None,
    ) -> Sequence[Enrollment]:
        """Get all enrollments in a group."""
        pass
    
    @abstractmethod
    async def get_academic_history(
        self,
        student_id: int,
    ) -> Sequence[Enrollment]:
        """Get complete academic history for a student."""
        pass
    
    @abstractmethod
    async def get_current_enrollments(
        self,
        student_id: int,
    ) -> Sequence[Enrollment]:
        """Get current active enrollments for a student."""
        pass
    
    @abstractmethod
    async def count_attempts(
        self,
        student_id: int,
        subject_id: int,
    ) -> int:
        """Count how many times a student has attempted a subject."""
        pass
    
    @abstractmethod
    async def has_passed_subject(
        self,
        student_id: int,
        subject_id: int,
    ) -> bool:
        """Check if student has passed a specific subject."""
        pass
