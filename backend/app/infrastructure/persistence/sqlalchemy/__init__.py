"""SQLAlchemy-specific adapters package."""
from app.infrastructure.persistence.sqlalchemy.user_repository_impl import SQLAlchemyUserRepository
from app.infrastructure.persistence.sqlalchemy.role_repository_impl import SQLAlchemyRoleRepository
from app.infrastructure.persistence.sqlalchemy.subject_repository_impl import SQLAlchemySubjectRepository
from app.infrastructure.persistence.sqlalchemy.group_repository_impl import SQLAlchemyGroupRepository
from app.infrastructure.persistence.sqlalchemy.enrollment_repository_impl import SQLAlchemyEnrollmentRepository
from app.infrastructure.persistence.sqlalchemy.assignment_repository_impl import SQLAlchemyAssignmentRepository
from app.infrastructure.persistence.sqlalchemy.internship_repository_impl import (
    SQLAlchemyCompanyRepository,
    SQLAlchemyPositionRepository,
    SQLAlchemyApplicationRepository,
    SQLAlchemyInternshipRepository,
    SQLAlchemyReportRepository,
)
from app.infrastructure.persistence.sqlalchemy.reservation_repository_impl import (
    SQLAlchemyResourceRepository,
    SQLAlchemyReservationRepository,
    SQLAlchemyRuleRepository,
)


__all__ = [
    "SQLAlchemyUserRepository",
    "SQLAlchemyRoleRepository",
    "SQLAlchemySubjectRepository",
    "SQLAlchemyGroupRepository",
    "SQLAlchemyEnrollmentRepository",
    "SQLAlchemyAssignmentRepository",
    "SQLAlchemyCompanyRepository",
    "SQLAlchemyPositionRepository",
    "SQLAlchemyApplicationRepository",
    "SQLAlchemyInternshipRepository",
    "SQLAlchemyReportRepository",
    "SQLAlchemyResourceRepository",
    "SQLAlchemyReservationRepository",
    "SQLAlchemyRuleRepository",
]
