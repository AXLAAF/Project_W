"""
FastAPI dependencies for the Hexagonal Architecture API.
Injects Use Cases and Domain objects into Routers.
"""
from typing import Annotated, List, Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database import get_db
from app.domain.entities.user import User

# Repositories
from app.domain.repositories.user_repository import IUserRepository
from app.domain.repositories.role_repository import IRoleRepository
from app.domain.repositories.subject_repository import ISubjectRepository
from app.domain.repositories.group_repository import IGroupRepository
from app.domain.repositories.period_repository import IPeriodRepository
from app.infrastructure.persistence.sqlalchemy.user_repository_impl import SQLAlchemyUserRepository
from app.infrastructure.persistence.sqlalchemy.role_repository_impl import SQLAlchemyRoleRepository

# Services
from app.domain.services.password_service import IPasswordService
from app.domain.services.token_service import ITokenService
from app.infrastructure.services.password_service_impl import PasswordServiceImpl
from app.infrastructure.services.token_service_impl import TokenServiceImpl

# Use Cases
from app.application.use_cases.login_user import LoginUserUseCase
from app.application.use_cases.register_user import RegisterUserUseCase
from app.application.use_cases.get_user_profile import GetUserProfileUseCase
from app.application.use_cases.update_profile import UpdateProfileUseCase
from app.application.use_cases.list_users import ListUsersUseCase
from app.application.use_cases.deactivate_user import DeactivateUserUseCase
from app.application.use_cases.assign_role import AssignRoleUseCase
from app.application.use_cases.remove_role import RemoveRoleUseCase
from app.application.use_cases.refresh_token import RefreshTokenUseCase

# Security
security = HTTPBearer()

from app.infrastructure.persistence.sqlalchemy.subject_repository_impl import SQLAlchemySubjectRepository

from app.application.use_cases.planning.subject.create_subject import CreateSubjectUseCase
from app.application.use_cases.planning.subject.get_subject import GetSubjectUseCase
from app.application.use_cases.planning.subject.list_subjects import ListSubjectsUseCase
from app.application.use_cases.planning.subject.update_subject import UpdateSubjectUseCase
from app.application.use_cases.planning.subject.add_prerequisite import AddPrerequisiteUseCase

# Group Use Cases
from app.application.use_cases.planning.group.list_groups import ListGroupsUseCase
from app.application.use_cases.planning.group.get_group import GetGroupUseCase
from app.application.use_cases.planning.group.create_group import CreateGroupUseCase

# Enrollment Use Cases
from app.application.use_cases.planning.enrollment.enroll_student import EnrollStudentUseCase
from app.application.use_cases.planning.enrollment.get_academic_history import GetAcademicHistoryUseCase
from app.application.use_cases.planning.enrollment.simulate_enrollment import SimulateEnrollmentUseCase
from app.application.use_cases.planning.enrollment.get_available_groups import GetAvailableGroupsUseCase

# --- Infrastructure Adapters ---

def get_user_repository(session: Annotated[AsyncSession, Depends(get_db)]) -> IUserRepository:
    return SQLAlchemyUserRepository(session)

def get_role_repository(session: Annotated[AsyncSession, Depends(get_db)]) -> IRoleRepository:
    return SQLAlchemyRoleRepository(session)

from app.infrastructure.persistence.sqlalchemy.group_repository_impl import SQLAlchemyGroupRepository
from app.infrastructure.persistence.sqlalchemy.period_repository_impl import SQLAlchemyPeriodRepository

def get_subject_repository(session: Annotated[AsyncSession, Depends(get_db)]) -> ISubjectRepository:
    return SQLAlchemySubjectRepository(session)

def get_group_repository(session: Annotated[AsyncSession, Depends(get_db)]) -> IGroupRepository:
    return SQLAlchemyGroupRepository(session)

def get_period_repository(session: Annotated[AsyncSession, Depends(get_db)]) -> IPeriodRepository:
    return SQLAlchemyPeriodRepository(session)

from app.infrastructure.persistence.sqlalchemy.enrollment_repository_impl import SQLAlchemyEnrollmentRepository
from app.domain.repositories.enrollment_repository import IEnrollmentRepository

def get_enrollment_repository(session: Annotated[AsyncSession, Depends(get_db)]) -> IEnrollmentRepository:
    return SQLAlchemyEnrollmentRepository(session)

# Planning Use Case Factories for Groups and Enrollments

def get_list_groups_use_case(
    group_repo: Annotated[IGroupRepository, Depends(get_group_repository)],
    period_repo: Annotated[IPeriodRepository, Depends(get_period_repository)],
) -> ListGroupsUseCase:
    return ListGroupsUseCase(group_repo, period_repo)

def get_get_group_use_case(
    group_repo: Annotated[IGroupRepository, Depends(get_group_repository)],
) -> GetGroupUseCase:
    return GetGroupUseCase(group_repo)

def get_create_group_use_case(
    group_repo: Annotated[IGroupRepository, Depends(get_group_repository)],
) -> CreateGroupUseCase:
    return CreateGroupUseCase(group_repo)

def get_enroll_student_use_case(
    enrollment_repo: Annotated[IEnrollmentRepository, Depends(get_enrollment_repository)],
    group_repo: Annotated[IGroupRepository, Depends(get_group_repository)],
    subject_repo: Annotated[ISubjectRepository, Depends(get_subject_repository)],
) -> EnrollStudentUseCase:
    return EnrollStudentUseCase(enrollment_repo, group_repo, subject_repo)

def get_get_academic_history_use_case(
    enrollment_repo: Annotated[IEnrollmentRepository, Depends(get_enrollment_repository)],
) -> GetAcademicHistoryUseCase:
    return GetAcademicHistoryUseCase(enrollment_repo)

def get_simulate_enrollment_use_case(
    enrollment_repo: Annotated[IEnrollmentRepository, Depends(get_enrollment_repository)],
    group_repo: Annotated[IGroupRepository, Depends(get_group_repository)],
    subject_repo: Annotated[ISubjectRepository, Depends(get_subject_repository)],
) -> SimulateEnrollmentUseCase:
    return SimulateEnrollmentUseCase(enrollment_repo, group_repo, subject_repo)

def get_get_available_groups_use_case(
    enrollment_repo: Annotated[IEnrollmentRepository, Depends(get_enrollment_repository)],
    group_repo: Annotated[IGroupRepository, Depends(get_group_repository)],
    subject_repo: Annotated[ISubjectRepository, Depends(get_subject_repository)],
) -> GetAvailableGroupsUseCase:
    return GetAvailableGroupsUseCase(enrollment_repo, group_repo, subject_repo)

# ... (Previous Core Factories)

# --- Planning Use Cases ---

def get_create_subject_use_case(
    repo: Annotated[ISubjectRepository, Depends(get_subject_repository)]
) -> CreateSubjectUseCase:
    return CreateSubjectUseCase(repo)

def get_get_subject_use_case(
    repo: Annotated[ISubjectRepository, Depends(get_subject_repository)]
) -> GetSubjectUseCase:
    return GetSubjectUseCase(repo)

def get_list_subjects_use_case(
    repo: Annotated[ISubjectRepository, Depends(get_subject_repository)]
) -> ListSubjectsUseCase:
    return ListSubjectsUseCase(repo)

def get_update_subject_use_case(
    repo: Annotated[ISubjectRepository, Depends(get_subject_repository)]
) -> UpdateSubjectUseCase:
    return UpdateSubjectUseCase(repo)

def get_add_prerequisite_use_case(
    repo: Annotated[ISubjectRepository, Depends(get_subject_repository)]
) -> AddPrerequisiteUseCase:
    return AddPrerequisiteUseCase(repo)


def get_password_service() -> IPasswordService:
    return PasswordServiceImpl()

def get_token_service() -> ITokenService:
    return TokenServiceImpl()

# --- Use Cases ---

def get_login_use_case(
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
    password_service: Annotated[IPasswordService, Depends(get_password_service)],
    token_service: Annotated[ITokenService, Depends(get_token_service)],
) -> LoginUserUseCase:
    return LoginUserUseCase(user_repo, password_service, token_service)

def get_register_use_case(
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
    role_repo: Annotated[IRoleRepository, Depends(get_role_repository)],
    password_service: Annotated[IPasswordService, Depends(get_password_service)],
) -> RegisterUserUseCase:
    return RegisterUserUseCase(user_repo, role_repo, password_service)

def get_refresh_token_use_case(
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
    token_service: Annotated[ITokenService, Depends(get_token_service)],
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(user_repo, token_service)

def get_user_profile_use_case(
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
) -> GetUserProfileUseCase:
    return GetUserProfileUseCase(user_repo)

def get_update_profile_use_case(
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
) -> UpdateProfileUseCase:
    return UpdateProfileUseCase(user_repo)

def get_list_users_use_case(
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
) -> ListUsersUseCase:
    return ListUsersUseCase(user_repo)

def get_deactivate_user_use_case(
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
) -> DeactivateUserUseCase:
    return DeactivateUserUseCase(user_repo)

def get_assign_role_use_case(
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
    role_repo: Annotated[IRoleRepository, Depends(get_role_repository)],
) -> AssignRoleUseCase:
    return AssignRoleUseCase(user_repo, role_repo)

def get_remove_role_use_case(
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
    role_repo: Annotated[IRoleRepository, Depends(get_role_repository)],
) -> RemoveRoleUseCase:
    return RemoveRoleUseCase(user_repo, role_repo)

# --- Authentication Helpers ---

async def get_current_user(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
    token_service: Annotated[ITokenService, Depends(get_token_service)],
) -> User:
    """
    Get current user from JWT token. 
    This is an Adapter logic (HTTP/Token -> Domain Entity).
    """
    payload = token_service.decode_token(token.credentials)
    if not payload or not token_service.verify_token_type(payload, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
        
    user = await user_repo.get_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is deactivated")
        
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Role checkers
def require_roles(required_roles: List[str]):
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        # Check domain user roles
        user_role_names = current_user.get_role_names()
        if not any(role in user_role_names for role in required_roles):
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return role_checker

require_admin = require_roles(["ADMIN_SISTEMA"])
require_coordinator = require_roles(["ADMIN_SISTEMA", "COORDINADOR"])

# --- Risk Module Dependencies ---

from app.domain.repositories.risk_repository import IRiskRepository
from app.infrastructure.persistence.sqlalchemy.risk_repository_impl import SQLAlchemyRiskRepository
from app.domain.ports.risk_model_port import IRiskModelPort
from app.infrastructure.ml.sklearn_risk_model import SklearnRiskModelAdapter
from app.application.use_cases.risk.calculate_risk import CalculateRiskScoreUseCase

def get_risk_repository(session: Annotated[AsyncSession, Depends(get_db)]) -> IRiskRepository:
    return SQLAlchemyRiskRepository(session)

def get_risk_model() -> IRiskModelPort:
    # Initialize with default config (mock for now)
    return SklearnRiskModelAdapter()

def get_calculate_risk_score_use_case(
    risk_repo: Annotated[IRiskRepository, Depends(get_risk_repository)],
    risk_model: Annotated[IRiskModelPort, Depends(get_risk_model)],
) -> CalculateRiskScoreUseCase:
    return CalculateRiskScoreUseCase(risk_repo, risk_model)

# Placeholders for future use cases to avoid import errors in router
def get_risk_history_use_case():
    return None

def get_group_risk_statistics_use_case():
    return None
