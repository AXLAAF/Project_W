"""
InternshipApplication repository for database operations.
"""
from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.internships.models.internship_application import InternshipApplication, ApplicationStatus
from app.internships.models.internship_position import InternshipPosition


class ApplicationRepository:
    """Repository for InternshipApplication database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, application_id: int) -> Optional[InternshipApplication]:
        """Get application by ID with position and user."""
        query = (
            select(InternshipApplication)
            .options(
                selectinload(InternshipApplication.position).selectinload(InternshipPosition.company),
                selectinload(InternshipApplication.user),
                selectinload(InternshipApplication.internship),
            )
            .where(InternshipApplication.id == application_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user_and_position(
        self, user_id: int, position_id: int
    ) -> Optional[InternshipApplication]:
        """Check if user already applied to a position."""
        query = select(InternshipApplication).where(
            InternshipApplication.user_id == user_id,
            InternshipApplication.position_id == position_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: int,
        offset: int = 0,
        limit: int = 20,
        status: Optional[ApplicationStatus] = None,
    ) -> tuple[Sequence[InternshipApplication], int]:
        """Get all applications for a user."""
        query = (
            select(InternshipApplication)
            .options(
                selectinload(InternshipApplication.position).selectinload(InternshipPosition.company),
            )
            .where(InternshipApplication.user_id == user_id)
        )
        count_query = (
            select(func.count())
            .select_from(InternshipApplication)
            .where(InternshipApplication.user_id == user_id)
        )

        if status is not None:
            query = query.where(InternshipApplication.status == status)
            count_query = count_query.where(InternshipApplication.status == status)

        query = query.offset(offset).limit(limit).order_by(InternshipApplication.applied_at.desc())

        result = await self.session.execute(query)
        count_result = await self.session.execute(count_query)

        return result.scalars().all(), count_result.scalar_one()

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        status: Optional[ApplicationStatus] = None,
        position_id: Optional[int] = None,
    ) -> tuple[Sequence[InternshipApplication], int]:
        """Get all applications with pagination (for admin/reviewer)."""
        query = select(InternshipApplication).options(
            selectinload(InternshipApplication.position).selectinload(InternshipPosition.company),
            selectinload(InternshipApplication.user),
        )
        count_query = select(func.count()).select_from(InternshipApplication)

        if status is not None:
            query = query.where(InternshipApplication.status == status)
            count_query = count_query.where(InternshipApplication.status == status)

        if position_id is not None:
            query = query.where(InternshipApplication.position_id == position_id)
            count_query = count_query.where(InternshipApplication.position_id == position_id)

        query = query.offset(offset).limit(limit).order_by(InternshipApplication.applied_at.desc())

        result = await self.session.execute(query)
        count_result = await self.session.execute(count_query)

        return result.scalars().all(), count_result.scalar_one()

    async def create(self, **kwargs) -> InternshipApplication:
        """Create a new application."""
        application = InternshipApplication(**kwargs)
        self.session.add(application)
        await self.session.flush()
        return application

    async def update_status(
        self,
        application: InternshipApplication,
        status: ApplicationStatus,
        reviewer_id: int,
        reviewer_notes: Optional[str] = None,
    ) -> InternshipApplication:
        """Update application status."""
        application.status = status
        application.reviewer_id = reviewer_id
        application.reviewer_notes = reviewer_notes
        application.reviewed_at = datetime.utcnow()
        await self.session.flush()
        return application

    async def delete(self, application: InternshipApplication) -> None:
        """Delete an application."""
        await self.session.delete(application)
