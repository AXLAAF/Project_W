"""
SQLAlchemy implementation of Internship repositories.
"""
from typing import Optional, Sequence
from datetime import date

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.internship.company import Company
from app.domain.entities.internship.position import InternshipPosition
from app.domain.entities.internship.application import InternshipApplication
from app.domain.entities.internship.internship import Internship
from app.domain.entities.internship.report import InternshipReport

from app.domain.repositories.internship_repository import (
    ICompanyRepository,
    IPositionRepository,
    IApplicationRepository,
    IInternshipRepository,
    IReportRepository,
)
from app.domain.value_objects.internship import (
    CompanyStatus,
    ApplicationStatus,
    InternshipStatus,
    ReportStatus,
)

from app.infrastructure.persistence.sqlalchemy.internship_mappers import (
    CompanyMapper,
    PositionMapper,
    ApplicationMapper,
    InternshipMapper,
    ReportMapper,
)

from app.internships.models.company import Company as CompanyModel
from app.internships.models.internship_position import InternshipPosition as PositionModel
from app.internships.models.internship_application import InternshipApplication as ApplicationModel
from app.internships.models.internship import Internship as InternshipModel
from app.internships.models.internship_report import InternshipReport as ReportModel


class SQLAlchemyCompanyRepository(ICompanyRepository):
    """SQLAlchemy implementation of Company repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, company_id: int) -> Optional[Company]:
        result = await self.session.execute(
            select(CompanyModel).where(CompanyModel.id == company_id)
        )
        model = result.scalar_one_or_none()
        return CompanyMapper.to_entity(model) if model else None

    async def get_by_rfc(self, rfc: str) -> Optional[Company]:
        result = await self.session.execute(
            select(CompanyModel).where(CompanyModel.rfc == rfc)
        )
        model = result.scalar_one_or_none()
        return CompanyMapper.to_entity(model) if model else None

    async def save(self, company: Company) -> Company:
        model = CompanyMapper.to_model(company)
        self.session.add(model)
        await self.session.flush()
        return CompanyMapper.to_entity(model)

    async def update(self, company: Company) -> Company:
        if company.id is None:
            raise ValueError("Company ID is required for update")
            
        result = await self.session.execute(
            select(CompanyModel).where(CompanyModel.id == company.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Company {company.id} not found")
            
        # Update fields
        model.name = company.name
        model.contact_email = company.contact_email
        model.contact_phone = company.contact_phone
        model.address = company.address
        model.description = company.description
        model.website = company.website
        model.logo_url = company.logo_url
        model.is_verified = company.is_verified
        model.is_active = (company.status == CompanyStatus.ACTIVE)
        
        await self.session.flush()
        return CompanyMapper.to_entity(model)

    async def list_companies(self, status: Optional[CompanyStatus] = None) -> Sequence[Company]:
        stmt = select(CompanyModel)
        if status == CompanyStatus.ACTIVE:
            stmt = stmt.where(CompanyModel.is_active == True)
        elif status == CompanyStatus.INACTIVE:
            stmt = stmt.where(CompanyModel.is_active == False)
            
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [CompanyMapper.to_entity(m) for m in models]


class SQLAlchemyPositionRepository(IPositionRepository):
    """SQLAlchemy implementation of Position repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, position_id: int) -> Optional[InternshipPosition]:
        result = await self.session.execute(
            select(PositionModel).where(PositionModel.id == position_id)
        )
        model = result.scalar_one_or_none()
        return PositionMapper.to_entity(model) if model else None

    async def save(self, position: InternshipPosition) -> InternshipPosition:
        model = PositionMapper.to_model(position)
        self.session.add(model)
        await self.session.flush()
        return PositionMapper.to_entity(model)

    async def update(self, position: InternshipPosition) -> InternshipPosition:
        if position.id is None:
            raise ValueError("Position ID is required for update")
            
        result = await self.session.execute(
            select(PositionModel).where(PositionModel.id == position.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Position {position.id} not found")
            
        # Update fields
        model.title = position.title
        model.description = position.description
        model.requirements = position.requirements
        model.location = position.location
        model.is_active = position.is_active
        
        await self.session.flush()
        return PositionMapper.to_entity(model)

    async def list_open_positions(self) -> Sequence[InternshipPosition]:
        result = await self.session.execute(
            select(PositionModel).where(PositionModel.is_active == True)
        )
        models = result.scalars().all()
        return [PositionMapper.to_entity(m) for m in models]

    async def list_by_company(self, company_id: int) -> Sequence[InternshipPosition]:
        result = await self.session.execute(
            select(PositionModel).where(PositionModel.company_id == company_id)
        )
        models = result.scalars().all()
        return [PositionMapper.to_entity(m) for m in models]


class SQLAlchemyApplicationRepository(IApplicationRepository):
    """SQLAlchemy implementation of Application repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, application_id: int) -> Optional[InternshipApplication]:
        result = await self.session.execute(
            select(ApplicationModel).where(ApplicationModel.id == application_id)
        )
        model = result.scalar_one_or_none()
        return ApplicationMapper.to_entity(model) if model else None

    async def get_by_student_and_position(self, student_id: int, position_id: int) -> Optional[InternshipApplication]:
        result = await self.session.execute(
            select(ApplicationModel).where(
                ApplicationModel.user_id == student_id,
                ApplicationModel.position_id == position_id
            )
        )
        model = result.scalar_one_or_none()
        return ApplicationMapper.to_entity(model) if model else None

    async def save(self, application: InternshipApplication) -> InternshipApplication:
        model = ApplicationMapper.to_model(application)
        self.session.add(model)
        await self.session.flush()
        return ApplicationMapper.to_entity(model)

    async def update(self, application: InternshipApplication) -> InternshipApplication:
        if application.id is None:
            raise ValueError("Application ID is required for update")
            
        result = await self.session.execute(
            select(ApplicationModel).where(ApplicationModel.id == application.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Application {application.id} not found")
            
        model.status = application.status.value.lower()
        model.reviewed_by = application.reviewed_by
        model.reviewed_at = application.reviewed_at
        model.reviewer_notes = application.comments
        
        await self.session.flush()
        return ApplicationMapper.to_entity(model)

    async def list_by_student(self, student_id: int) -> Sequence[InternshipApplication]:
        result = await self.session.execute(
            select(ApplicationModel).where(ApplicationModel.user_id == student_id)
        )
        models = result.scalars().all()
        return [ApplicationMapper.to_entity(m) for m in models]

    async def list_by_position(self, position_id: int, status: Optional[ApplicationStatus] = None) -> Sequence[InternshipApplication]:
        stmt = select(ApplicationModel).where(ApplicationModel.position_id == position_id)
        if status:
            stmt = stmt.where(ApplicationModel.status == status.value.lower())
            
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [ApplicationMapper.to_entity(m) for m in models]


class SQLAlchemyInternshipRepository(IInternshipRepository):
    """SQLAlchemy implementation of Internship repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, internship_id: int) -> Optional[Internship]:
        result = await self.session.execute(
            select(InternshipModel).where(InternshipModel.id == internship_id)
        )
        model = result.scalar_one_or_none()
        return InternshipMapper.to_entity(model) if model else None
        
    async def get_by_application(self, application_id: int) -> Optional[Internship]:
        result = await self.session.execute(
            select(InternshipModel).where(InternshipModel.application_id == application_id)
        )
        model = result.scalar_one_or_none()
        return InternshipMapper.to_entity(model) if model else None

    async def save(self, internship: Internship) -> Internship:
        model = InternshipMapper.to_model(internship)
        self.session.add(model)
        await self.session.flush()
        return InternshipMapper.to_entity(model)

    async def update(self, internship: Internship) -> Internship:
        if internship.id is None:
            raise ValueError("Internship ID is required for update")
            
        result = await self.session.execute(
            select(InternshipModel).where(InternshipModel.id == internship.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Internship {internship.id} not found")
            
        model.status = internship.status.value.lower()
        model.actual_end_date = internship.actual_end_date
        model.total_hours = internship.total_hours
        model.final_grade = internship.final_grade
        model.completion_certificate_path = internship.completion_certificate_path
        
        await self.session.flush()
        return InternshipMapper.to_entity(model)

    async def list_active_by_student(self, student_id: int) -> Sequence[Internship]:
        stmt = (
            select(InternshipModel)
            .join(ApplicationModel, InternshipModel.application_id == ApplicationModel.id)
            .where(
                ApplicationModel.user_id == student_id,
                InternshipModel.status == 'active'
            )
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [InternshipMapper.to_entity(m) for m in models]


class SQLAlchemyReportRepository(IReportRepository):
    """SQLAlchemy implementation of Report repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, report_id: int) -> Optional[InternshipReport]:
        result = await self.session.execute(
            select(ReportModel).where(ReportModel.id == report_id)
        )
        model = result.scalar_one_or_none()
        return ReportMapper.to_entity(model) if model else None

    async def save(self, report: InternshipReport) -> InternshipReport:
        model = ReportMapper.to_model(report)
        self.session.add(model)
        await self.session.flush()
        return ReportMapper.to_entity(model)

    async def update(self, report: InternshipReport) -> InternshipReport:
        if report.id is None:
            raise ValueError("Report ID is required for update")
            
        result = await self.session.execute(
            select(ReportModel).where(ReportModel.id == report.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Report {report.id} not found")
        
        model.status = report.status.value.lower()
        model.hours_worked = report.hours_logged
        model.activities_summary = report.content
        model.supervisor_comments = report.comments
        model.reviewed_at = report.reviewed_at
        
        await self.session.flush()
        return ReportMapper.to_entity(model)

    async def list_by_internship(self, internship_id: int) -> Sequence[InternshipReport]:
        result = await self.session.execute(
            select(ReportModel).where(ReportModel.internship_id == internship_id)
            .order_by(ReportModel.report_date)
        )
        models = result.scalars().all()
        return [ReportMapper.to_entity(m) for m in models]
