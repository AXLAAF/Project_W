"""
Subject repository interface (port).
Defines the contract for subject persistence operations.
"""
from abc import ABC, abstractmethod
from typing import Optional, Sequence, Tuple

from app.domain.entities.planning.subject import Subject


class ISubjectRepository(ABC):
    """
    Abstract interface for subject repository.
    
    This is a 'port' in hexagonal architecture terminology.
    """
    
    @abstractmethod
    async def get_by_id(self, subject_id: int) -> Optional[Subject]:
        """Get a subject by ID."""
        pass
    
    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[Subject]:
        """Get a subject by its code."""
        pass
    
    @abstractmethod
    async def save(self, subject: Subject) -> Subject:
        """Save a new subject."""
        pass
    
    @abstractmethod
    async def update(self, subject: Subject) -> Subject:
        """Update an existing subject."""
        pass
    
    @abstractmethod
    async def delete(self, subject_id: int) -> bool:
        """Delete a subject."""
        pass
    
    @abstractmethod
    async def list_all(
        self,
        offset: int = 0,
        limit: int = 50,
        department: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[Sequence[Subject], int]:
        """
        List subjects with filtering and pagination.
        
        Returns:
            Tuple of (list of subjects, total count)
        """
        pass
    
    @abstractmethod
    async def get_prerequisites(self, subject_id: int) -> Sequence[Subject]:
        """Get all prerequisites for a subject."""
        pass
    
    @abstractmethod
    async def get_available_for_student(
        self,
        student_id: int,
        period_id: int,
    ) -> Sequence[Subject]:
        """
        Get subjects available for a student to enroll in.
        Considers completed subjects and prerequisites.
        """
        pass
