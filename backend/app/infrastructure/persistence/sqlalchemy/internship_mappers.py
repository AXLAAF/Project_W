"""
Internship module mappers.
Translate between SQLAlchemy ORM models and domain entities.
"""
from typing import Optional, List
from datetime import datetime

from app.internships.models.company import Company as CompanyModel
from app.internships.models.internship_position import InternshipPosition as PositionModel
from app.internships.models.internship_application import InternshipApplication as ApplicationModel
from app.internships.models.internship import Internship as InternshipModel
from app.internships.models.internship_report import InternshipReport as ReportModel

from app.domain.entities.internship.company import Company as CompanyEntity
from app.domain.entities.internship.position import InternshipPosition as PositionEntity
from app.domain.entities.internship.application import InternshipApplication as ApplicationEntity
from app.domain.entities.internship.internship import Internship as InternshipEntity
from app.domain.entities.internship.report import InternshipReport as ReportEntity

from app.domain.value_objects.internship import (
    ApplicationStatus,
    InternshipStatus,
    ReportStatus,
    ReportType,
    CompanyStatus,
)


class CompanyMapper:
    """Mapper for Company entity <-> model."""
    
    @staticmethod
    def to_entity(model: CompanyModel) -> CompanyEntity:
        entity = CompanyEntity(
            id=model.id,
            name=model.name,
            rfc=model.rfc,
            contact_email=model.contact_email,
            contact_phone=model.contact_phone,
            address=model.address,
            description=model.description,
            website=model.website,
            logo_url=model.logo_url,
            is_verified=model.is_verified,
            created_at=model.created_at,
        )
        if not model.is_active:
            entity.status = CompanyStatus.INACTIVE
        return entity

    @staticmethod
    def to_model(entity: CompanyEntity) -> CompanyModel:
        return CompanyModel(
            id=entity.id,
            name=entity.name,
            rfc=entity.rfc,
            contact_email=entity.contact_email,
            contact_phone=entity.contact_phone,
            address=entity.address,
            description=entity.description,
            website=entity.website,
            logo_url=entity.logo_url,
            is_verified=entity.is_verified,
            is_active=entity.status == CompanyStatus.ACTIVE,
        )


class PositionMapper:
    """Mapper for InternshipPosition entity <-> model."""
    
    @staticmethod
    def to_entity(model: PositionModel) -> PositionEntity:
        return PositionEntity(
            id=model.id,
            company_id=model.company_id,
            title=model.title,
            description=model.description,
            requirements=model.requirements or "",
            location=model.location,
            salary=None,  # Not in legacy model?
            is_active=model.is_active,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: PositionEntity) -> PositionModel:
        return PositionModel(
            id=entity.id,
            company_id=entity.company_id,
            title=entity.title,
            description=entity.description,
            requirements=entity.requirements,
            location=entity.location,
            is_active=entity.is_active,
        )


class ApplicationMapper:
    """Mapper for InternshipApplication entity <-> model."""
    
    @staticmethod
    def to_entity(model: ApplicationModel) -> ApplicationEntity:
        return ApplicationEntity(
            id=model.id,
            student_id=model.user_id,
            position_id=model.position_id,
            cv_url=model.cv_path,
            cover_letter=model.cover_letter,
            status=ApplicationStatus(model.status.value.upper()),
            reviewed_by=model.reviewer_id,
            reviewed_at=model.reviewed_at,
            comments=model.reviewer_notes,
            submitted_at=model.applied_at,
        )

    @staticmethod
    def to_model(entity: ApplicationEntity) -> ApplicationModel:
        return ApplicationModel(
            id=entity.id,
            user_id=entity.student_id,
            position_id=entity.position_id,
            cv_path=entity.cv_url,
            cover_letter=entity.cover_letter,
            status=entity.status.value.lower(),  # Enum conversion if needed
            reviewer_id=entity.reviewed_by,
            reviewed_at=entity.reviewed_at,
            reviewer_notes=entity.comments,
        )


class InternshipMapper:
    """Mapper for Internship entity <-> model."""
    
    @staticmethod
    def to_entity(model: InternshipModel) -> InternshipEntity:
        return InternshipEntity(
            id=model.id,
            application_id=model.application_id,
            start_date=model.start_date,
            expected_end_date=model.expected_end_date,
            supervisor_name=model.supervisor_name,
            supervisor_email=model.supervisor_email,
            supervisor_phone=model.supervisor_phone,
            status=InternshipStatus(model.status.value.upper()),
            actual_end_date=model.actual_end_date,
            total_hours=model.total_hours,
            final_grade=model.final_grade,
            completion_certificate_path=model.completion_certificate_path,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: InternshipEntity) -> InternshipModel:
        return InternshipModel(
            id=entity.id,
            application_id=entity.application_id,
            start_date=entity.start_date,
            expected_end_date=entity.expected_end_date,
            supervisor_name=entity.supervisor_name,
            supervisor_email=entity.supervisor_email,
            supervisor_phone=entity.supervisor_phone,
            status=entity.status.value.lower(),
            actual_end_date=entity.actual_end_date,
            total_hours=entity.total_hours,
            final_grade=entity.final_grade,
            completion_certificate_path=entity.completion_certificate_path,
        )


class ReportMapper:
    """Mapper for InternshipReport entity <-> model."""
    
    @staticmethod
    def to_entity(model: ReportModel) -> ReportEntity:
        # Determine ReportType usually by month_number or logic, assuming PARTIAL
        # Legacy model has month_number.
        return ReportEntity(
            id=model.id,
            internship_id=model.internship_id,
            report_type=ReportType.PARTIAL,  # Defaulting
            start_date=model.report_date,  # Approximation
            end_date=model.report_date,    # Approximation
            content=model.activities_summary or "",
            hours_logged=model.hours_worked,
            status=ReportStatus(model.status.value.upper()),
            file_url=model.file_path,
            reviewed_at=model.reviewed_at,
            comments=model.supervisor_comments,
            submitted_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: ReportEntity) -> ReportModel:
        return ReportModel(
            id=entity.id,
            internship_id=entity.internship_id,
            month_number=1, # Default or calc
            report_date=entity.end_date,
            file_path=entity.file_url,
            hours_worked=entity.hours_logged,
            activities_summary=entity.content,
            status=entity.status.value.lower(),
            reviewed_at=entity.reviewed_at,
            supervisor_comments=entity.comments,
        )
