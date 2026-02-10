"""Domain repository interfaces (ports) package."""
from app.domain.repositories.user_repository import IUserRepository
from app.domain.repositories.role_repository import IRoleRepository
from app.domain.repositories.audit_log_repository import IAuditLogRepository
from app.domain.repositories.subject_repository import ISubjectRepository
from app.domain.repositories.group_repository import IGroupRepository
from app.domain.repositories.enrollment_repository import IEnrollmentRepository
from app.domain.repositories.risk_repository import IRiskRepository

__all__ = [
    "IUserRepository", "IRoleRepository", "IAuditLogRepository",
    "ISubjectRepository", "IGroupRepository", "IEnrollmentRepository",
    "IRiskRepository",
    "ICompanyRepository", "IPositionRepository",
    "IApplicationRepository", "IInternshipRepository",
]

