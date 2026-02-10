"""
Interface for academic period repository.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from app.domain.entities.planning.academic_period import AcademicPeriod

class IPeriodRepository(ABC):
    @abstractmethod
    async def get_current_period(self) -> Optional[AcademicPeriod]:
        """Get the currently active academic period."""
        pass

    @abstractmethod
    async def get_by_id(self, period_id: int) -> Optional[AcademicPeriod]:
        """Get an academic period by ID."""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[AcademicPeriod]:
        """List all academic periods."""
        pass
