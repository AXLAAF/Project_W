"""
Internship and InternshipReport repository for database operations.
"""
from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.internships.models.internship import Internship, InternshipStatus
from app.internships.models.internship_report import InternshipReport, ReportStatus
from app.internships.models.internship_application import InternshipApplication


class InternshipRepository:
    """Repository for Internship database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, internship_id: int) -> Optional[Internship]:
        """Get internship by ID with reports and application."""
        query = (
            select(Internship)
            .options(
                selectinload(Internship.reports),
                selectinload(Internship.application).selectinload(InternshipApplication.position),
                selectinload(Internship.application).selectinload(InternshipApplication.user),
            )
            .where(Internship.id == internship_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_application(self, application_id: int) -> Optional[Internship]:
        """Get internship by application ID."""
        query = (
            select(Internship)
            .options(selectinload(Internship.reports))
            .where(Internship.application_id == application_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: int,
        status: Optional[InternshipStatus] = None,
    ) -> Sequence[Internship]:
        """Get all internships for a user."""
        query = (
            select(Internship)
            .join(InternshipApplication)
            .options(
                selectinload(Internship.reports),
                selectinload(Internship.application).selectinload(InternshipApplication.position),
            )
            .where(InternshipApplication.user_id == user_id)
        )

        if status is not None:
            query = query.where(Internship.status == status)

        query = query.order_by(Internship.start_date.desc())

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        status: Optional[InternshipStatus] = None,
    ) -> tuple[Sequence[Internship], int]:
        """Get all internships with pagination."""
        query = select(Internship).options(
            selectinload(Internship.application).selectinload(InternshipApplication.user),
            selectinload(Internship.application).selectinload(InternshipApplication.position),
        )
        count_query = select(func.count()).select_from(Internship)

        if status is not None:
            query = query.where(Internship.status == status)
            count_query = count_query.where(Internship.status == status)

        query = query.offset(offset).limit(limit).order_by(Internship.start_date.desc())

        result = await self.session.execute(query)
        count_result = await self.session.execute(count_query)

        return result.scalars().all(), count_result.scalar_one()

    async def create(self, **kwargs) -> Internship:
        """Create a new internship."""
        internship = Internship(**kwargs)
        self.session.add(internship)
        await self.session.flush()
        return internship

    async def update(self, internship: Internship, **kwargs) -> Internship:
        """Update internship fields."""
        for key, value in kwargs.items():
            if hasattr(internship, key) and value is not None:
                setattr(internship, key, value)
        await self.session.flush()
        return internship

    async def complete(
        self,
        internship: Internship,
        actual_end_date,
        final_grade: float,
        total_hours: int,
    ) -> Internship:
        """Complete an internship."""
        internship.status = InternshipStatus.COMPLETED
        internship.actual_end_date = actual_end_date
        internship.final_grade = final_grade
        internship.total_hours = total_hours
        await self.session.flush()
        return internship

    # Report operations
    async def get_report_by_id(self, report_id: int) -> Optional[InternshipReport]:
        """Get report by ID."""
        query = select(InternshipReport).where(InternshipReport.id == report_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_reports_by_internship(self, internship_id: int) -> Sequence[InternshipReport]:
        """Get all reports for an internship."""
        query = (
            select(InternshipReport)
            .where(InternshipReport.internship_id == internship_id)
            .order_by(InternshipReport.month_number)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_report(self, **kwargs) -> InternshipReport:
        """Create a new report."""
        report = InternshipReport(**kwargs)
        self.session.add(report)
        await self.session.flush()
        return report

    async def update_report(self, report: InternshipReport, **kwargs) -> InternshipReport:
        """Update report fields."""
        for key, value in kwargs.items():
            if hasattr(report, key) and value is not None:
                setattr(report, key, value)
        await self.session.flush()
        return report

    async def submit_report(self, report: InternshipReport) -> InternshipReport:
        """Submit report for review."""
        report.status = ReportStatus.SUBMITTED
        report.submitted_at = datetime.utcnow()
        await self.session.flush()
        return report

    async def review_report(
        self,
        report: InternshipReport,
        status: ReportStatus,
        supervisor_comments: Optional[str] = None,
        supervisor_grade: Optional[float] = None,
    ) -> InternshipReport:
        """Review a report."""
        report.status = status
        report.supervisor_comments = supervisor_comments
        report.supervisor_grade = supervisor_grade
        report.reviewed_at = datetime.utcnow()
        await self.session.flush()
        return report
