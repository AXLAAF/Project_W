"""
Application service for business logic.
"""
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User
from app.internships.models.internship_application import InternshipApplication, ApplicationStatus
from app.internships.repositories.application_repository import ApplicationRepository
from app.internships.repositories.position_repository import PositionRepository
from app.internships.schemas.application import ApplicationCreate


class ApplicationError(Exception):
    """Raised when application operation fails."""
    pass


class ApplicationService:
    """Service for application business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ApplicationRepository(session)
        self.position_repo = PositionRepository(session)

    async def get_by_id(self, application_id: int) -> Optional[InternshipApplication]:
        """Get application by ID."""
        return await self.repo.get_by_id(application_id)

    async def get_by_user(
        self,
        user_id: int,
        offset: int = 0,
        limit: int = 20,
        status: Optional[ApplicationStatus] = None,
    ) -> tuple[Sequence[InternshipApplication], int]:
        """Get all applications for a user."""
        return await self.repo.get_by_user(user_id, offset, limit, status)

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        status: Optional[ApplicationStatus] = None,
        position_id: Optional[int] = None,
    ) -> tuple[Sequence[InternshipApplication], int]:
        """Get all applications (for admin/reviewer)."""
        return await self.repo.get_all(offset, limit, status, position_id)

    async def apply(
        self,
        user: User,
        data: ApplicationCreate,
        user_gpa: Optional[float] = None,
        user_credits: Optional[int] = None,
    ) -> InternshipApplication:
        """Apply to an internship position."""
        # Check if position exists and is available
        position = await self.position_repo.get_by_id(data.position_id)
        if not position:
            raise ApplicationError("Position not found")
        if not position.is_active:
            raise ApplicationError("Position is no longer active")
        if not position.is_available:
            raise ApplicationError("Position has no available spots")

        # Check if user already applied
        existing = await self.repo.get_by_user_and_position(user.id, data.position_id)
        if existing:
            raise ApplicationError("You have already applied to this position")

        # Validate requirements
        if position.min_gpa and user_gpa and user_gpa < position.min_gpa:
            raise ApplicationError(f"Minimum GPA required: {position.min_gpa}")
        if position.min_credits and user_credits and user_credits < position.min_credits:
            raise ApplicationError(f"Minimum credits required: {position.min_credits}")

        return await self.repo.create(
            user_id=user.id,
            position_id=data.position_id,
            cv_path=data.cv_path,
            cover_letter=data.cover_letter,
            additional_documents=data.additional_documents,
        )

    async def approve(
        self,
        application_id: int,
        reviewer_id: int,
        notes: Optional[str] = None,
    ) -> InternshipApplication:
        """Approve an application."""
        application = await self.repo.get_by_id(application_id)
        if not application:
            raise ApplicationError("Application not found")
        if application.status != ApplicationStatus.PENDING and application.status != ApplicationStatus.UNDER_REVIEW:
            raise ApplicationError(f"Cannot approve application with status: {application.status}")

        # Check if position still has spots
        position = await self.position_repo.get_by_id(application.position_id)
        if position and not position.is_available:
            raise ApplicationError("Position has no more available spots")

        # Update application status
        application = await self.repo.update_status(
            application, ApplicationStatus.APPROVED, reviewer_id, notes
        )

        # Increment filled count
        if position:
            await self.position_repo.increment_filled_count(position)

        return application

    async def reject(
        self,
        application_id: int,
        reviewer_id: int,
        notes: Optional[str] = None,
    ) -> InternshipApplication:
        """Reject an application."""
        application = await self.repo.get_by_id(application_id)
        if not application:
            raise ApplicationError("Application not found")
        if application.status not in [ApplicationStatus.PENDING, ApplicationStatus.UNDER_REVIEW]:
            raise ApplicationError(f"Cannot reject application with status: {application.status}")

        return await self.repo.update_status(
            application, ApplicationStatus.REJECTED, reviewer_id, notes
        )

    async def cancel(self, application_id: int, user_id: int) -> InternshipApplication:
        """Cancel own application."""
        application = await self.repo.get_by_id(application_id)
        if not application:
            raise ApplicationError("Application not found")
        if application.user_id != user_id:
            raise ApplicationError("You can only cancel your own applications")
        if application.status not in [ApplicationStatus.PENDING, ApplicationStatus.UNDER_REVIEW]:
            raise ApplicationError("Cannot cancel application at this stage")

        return await self.repo.update_status(
            application, ApplicationStatus.CANCELLED, user_id, "Cancelled by applicant"
        )
