"""
Internship repository interfaces (Ports).
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Sequence
from datetime import date

from app.domain.entities.internship.company import Company
from app.domain.entities.internship.position import InternshipPosition
from app.domain.entities.internship.application import InternshipApplication
from app.domain.entities.internship.internship import Internship
from app.domain.entities.internship.report import InternshipReport
from app.domain.value_objects.internship import ApplicationStatus, InternshipStatus, CompanyStatus


class ICompanyRepository(ABC):
    """Interface for Company repository."""
    
    @abstractmethod
    async def get_by_id(self, company_id: int) -> Optional[Company]:
        """Get company by ID."""
        pass
        
    @abstractmethod
    async def get_by_rfc(self, rfc: str) -> Optional[Company]:
        """Get company by RFC."""
        pass

    @abstractmethod
    async def save(self, company: Company) -> Company:
        """Save a new company."""
        pass
        
    @abstractmethod
    async def update(self, company: Company) -> Company:
        """Update an existing company."""
        pass
        
    @abstractmethod
    async def list_companies(self, status: Optional[CompanyStatus] = None) -> Sequence[Company]:
        """List companies, optionally filtered by status."""
        pass


class IPositionRepository(ABC):
    """Interface for InternshipPosition repository."""
    
    @abstractmethod
    async def get_by_id(self, position_id: int) -> Optional[InternshipPosition]:
        """Get position by ID."""
        pass

    @abstractmethod
    async def save(self, position: InternshipPosition) -> InternshipPosition:
        """Save a new position."""
        pass
        
    @abstractmethod
    async def update(self, position: InternshipPosition) -> InternshipPosition:
        """Update an existing position."""
        pass

    @abstractmethod
    async def list_open_positions(self) -> Sequence[InternshipPosition]:
        """List all open positions."""
        pass
        
    @abstractmethod
    async def list_by_company(self, company_id: int) -> Sequence[InternshipPosition]:
        """List positions for a specific company."""
        pass


class IApplicationRepository(ABC):
    """Interface for InternshipApplication repository."""
    
    @abstractmethod
    async def get_by_id(self, application_id: int) -> Optional[InternshipApplication]:
        """Get application by ID."""
        pass

    @abstractmethod
    async def get_by_student_and_position(self, student_id: int, position_id: int) -> Optional[InternshipApplication]:
        """Get application by student and position."""
        pass

    @abstractmethod
    async def save(self, application: InternshipApplication) -> InternshipApplication:
        """Save a new application."""
        pass
        
    @abstractmethod
    async def update(self, application: InternshipApplication) -> InternshipApplication:
        """Update an existing application."""
        pass
        
    @abstractmethod
    async def list_by_student(self, student_id: int) -> Sequence[InternshipApplication]:
        """List applications for a student."""
        pass
        
    @abstractmethod
    async def list_by_position(self, position_id: int, status: Optional[ApplicationStatus] = None) -> Sequence[InternshipApplication]:
        """List applications for a position."""
        pass


class IInternshipRepository(ABC):
    """Interface for Internship repository."""
    
    @abstractmethod
    async def get_by_id(self, internship_id: int) -> Optional[Internship]:
        """Get internship by ID."""
        pass
        
    @abstractmethod
    async def get_by_application(self, application_id: int) -> Optional[Internship]:
        """Get internship by application ID."""
        pass

    @abstractmethod
    async def save(self, internship: Internship) -> Internship:
        """Save a new internship."""
        pass
        
    @abstractmethod
    async def update(self, internship: Internship) -> Internship:
        """Update an existing internship."""
        pass

    @abstractmethod
    async def list_active_by_student(self, student_id: int) -> Sequence[Internship]:
        """List active internships for a student."""
        pass


class IReportRepository(ABC):
    """Interface for InternshipReport repository."""
    
    @abstractmethod
    async def get_by_id(self, report_id: int) -> Optional[InternshipReport]:
        """Get report by ID."""
        pass

    @abstractmethod
    async def save(self, report: InternshipReport) -> InternshipReport:
        """Save a new report."""
        pass
        
    @abstractmethod
    async def update(self, report: InternshipReport) -> InternshipReport:
        """Update an existing report."""
        pass

    @abstractmethod
    async def list_by_internship(self, internship_id: int) -> Sequence[InternshipReport]:
        """List reports for an internship."""
        pass
