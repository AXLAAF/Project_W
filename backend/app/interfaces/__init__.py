"""
Dependency injection for hexagonal architecture.
Provides FastAPI dependencies that wire up use cases with their implementations.
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database import get_db

# Domain interfaces
from app.domain.repositories.user_repository import IUserRepository
from app.domain.repositories.role_repository import IRoleRepository
from app.domain.services.password_service import IPasswordService
from app.domain.services.token_service import ITokenService

# Infrastructure implementations
from app.infrastructure.persistence.sqlalchemy.user_repository_impl import SQLAlchemyUserRepository
from app.infrastructure.persistence.sqlalchemy.role_repository_impl import SQLAlchemyRoleRepository
from app.infrastructure.services.password_service_impl import PasswordServiceImpl
from app.infrastructure.services.token_service_impl import TokenServiceImpl

# Use cases
from app.application.use_cases.get_user_profile import GetUserProfileUseCase
from app.application.use_cases.update_profile import UpdateProfileUseCase
from app.application.use_cases.list_users import ListUsersUseCase
from app.application.use_cases.register_user import RegisterUserUseCase
from app.application.use_cases.login_user import LoginUserUseCase
from app.application.use_cases.deactivate_user import DeactivateUserUseCase
from app.application.use_cases.assign_role import AssignRoleUseCase
from app.application.use_cases.remove_role import RemoveRoleUseCase
from app.application.use_cases.refresh_token import RefreshTokenUseCase


# ============== Repository Dependencies ==============

def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> IUserRepository:
    """Get user repository implementation."""
    return SQLAlchemyUserRepository(session)


def get_role_repository(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> IRoleRepository:
    """Get role repository implementation."""
    return SQLAlchemyRoleRepository(session)


# ============== Service Dependencies ==============

def get_password_service() -> IPasswordService:
    """Get password service implementation."""
    return PasswordServiceImpl()


def get_token_service() -> ITokenService:
    """Get token service implementation."""
    return TokenServiceImpl()


# ============== Use Case Dependencies ==============

def get_user_profile_use_case(
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)]
) -> GetUserProfileUseCase:
    """Get GetUserProfile use case."""
    return GetUserProfileUseCase(user_repo)


def get_update_profile_use_case(
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)]
) -> UpdateProfileUseCase:
    """Get UpdateProfile use case."""
    return UpdateProfileUseCase(user_repo)


def get_list_users_use_case(
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)]
) -> ListUsersUseCase:
    """Get ListUsers use case."""
    return ListUsersUseCase(user_repo)


def get_register_user_use_case(
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
    role_repo: Annotated[IRoleRepository, Depends(get_role_repository)],
    password_service: Annotated[IPasswordService, Depends(get_password_service)],
) -> RegisterUserUseCase:
    """Get RegisterUser use case."""
    return RegisterUserUseCase(user_repo, role_repo, password_service)


def get_login_user_use_case(
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
    password_service: Annotated[IPasswordService, Depends(get_password_service)],
    token_service: Annotated[ITokenService, Depends(get_token_service)],
) -> LoginUserUseCase:
    """Get LoginUser use case."""
    return LoginUserUseCase(user_repo, password_service, token_service)


def get_deactivate_user_use_case(
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)]
) -> DeactivateUserUseCase:
    """Get DeactivateUser use case."""
    return DeactivateUserUseCase(user_repo)


def get_assign_role_use_case(
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
    role_repo: Annotated[IRoleRepository, Depends(get_role_repository)],
) -> AssignRoleUseCase:
    """Get AssignRole use case."""
    return AssignRoleUseCase(user_repo, role_repo)


def get_remove_role_use_case(
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
    role_repo: Annotated[IRoleRepository, Depends(get_role_repository)],
) -> RemoveRoleUseCase:
    """Get RemoveRole use case."""
    return RemoveRoleUseCase(user_repo, role_repo)


def get_refresh_token_use_case(
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
    token_service: Annotated[ITokenService, Depends(get_token_service)],
) -> RefreshTokenUseCase:
    """Get RefreshToken use case."""
    return RefreshTokenUseCase(user_repo, token_service)
