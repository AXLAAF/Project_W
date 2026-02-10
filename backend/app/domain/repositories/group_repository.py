"""
Group repository interface (port).
Defines the contract for group persistence operations.
"""
from abc import ABC, abstractmethod
from typing import Optional, Sequence, Tuple

from app.domain.entities.planning.group import Group


class IGroupRepository(ABC):
    """
    Abstract interface for group repository.
    
    This is a 'port' in hexagonal architecture terminology.
    """
    
    @abstractmethod
    async def get_by_id(self, group_id: int) -> Optional[Group]:
        """Get a group by ID."""
        pass
    
    @abstractmethod
    async def save(self, group: Group) -> Group:
        """Save a new group."""
        pass
    
    @abstractmethod
    async def update(self, group: Group) -> Group:
        """Update an existing group."""
        pass
    
    @abstractmethod
    async def delete(self, group_id: int) -> bool:
        """Delete a group."""
        pass
    
    @abstractmethod
    async def list_by_subject(
        self,
        subject_id: int,
        period_id: Optional[int] = None,
        is_active: bool = True,
    ) -> Sequence[Group]:
        """Get all groups for a subject, optionally filtered by period."""
        pass
    
    @abstractmethod
    async def list_by_period(
        self,
        period_id: int,
        offset: int = 0,
        limit: int = 50,
    ) -> Tuple[Sequence[Group], int]:
        """Get all groups in an academic period."""
        pass
    
    @abstractmethod
    async def list_by_professor(
        self,
        professor_id: int,
        period_id: Optional[int] = None,
    ) -> Sequence[Group]:
        """Get all groups taught by a professor."""
        pass
    
    @abstractmethod
    async def get_available_groups(
        self,
        subject_id: int,
        period_id: int,
    ) -> Sequence[Group]:
        """Get groups with available spots for enrollment."""
        pass
    
    @abstractmethod
    async def increment_enrolled(self, group_id: int) -> bool:
        """Increment enrolled count for a group."""
        pass
    
    @abstractmethod
    async def decrement_enrolled(self, group_id: int) -> bool:
        """Decrement enrolled count for a group."""
        pass
