"""
Risk Repository Interfaces.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Sequence

from app.domain.entities.risk.risk_assessment import RiskAssessment


class IRiskRepository(ABC):
    """Interface for Risk Assessment repository."""
    
    @abstractmethod
    async def save(self, assessment: RiskAssessment) -> RiskAssessment:
        """Save a risk assessment."""
        pass
    
    @abstractmethod
    async def get_by_student_and_group(self, student_id: int, group_id: int) -> Optional[RiskAssessment]:
        """Get latest risk assessment for a student in a group."""
        pass
    
    @abstractmethod
    async def get_history_by_student(self, student_id: int, limit: int = 10) -> List[RiskAssessment]:
        """Get risk assessment history for a student."""
        pass
    
    @abstractmethod
    async def get_high_risk_students(self, group_id: int) -> List[RiskAssessment]:
        """Get all students at high risk in a group."""
        pass


# Legacy / Placeholder interfaces for existing implementations
class IRiskAssessmentRepository(ABC):
    pass

class IAttendanceRepository(ABC):
    pass

class IGradeRepository(ABC):
    pass

class IAssignmentRepository(ABC):
    pass
