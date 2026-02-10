"""
Internship service for business logic.
"""
from datetime import date
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.internships.models.internship import Internship, InternshipStatus
from app.internships.models.internship_report import InternshipReport, ReportStatus
from app.internships.models.internship_application import ApplicationStatus
from app.internships.repositories.internship_repository import InternshipRepository
from app.internships.repositories.application_repository import ApplicationRepository
from app.internships.schemas.internship import InternshipCreate, InternshipComplete
from app.internships.schemas.report import ReportCreate, ReportReview


class InternshipError(Exception):
    """Raised when internship operation fails."""
    pass


class InternshipService:
    """Service for internship business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = InternshipRepository(session)
        self.application_repo = ApplicationRepository(session)

    async def get_by_id(self, internship_id: int) -> Optional[Internship]:
        """Get internship by ID."""
        return await self.repo.get_by_id(internship_id)

    async def get_by_user(
        self,
        user_id: int,
        status: Optional[InternshipStatus] = None,
    ) -> Sequence[Internship]:
        """Get all internships for a user."""
        return await self.repo.get_by_user(user_id, status)

    async def get_active_by_user(self, user_id: int) -> Optional[Internship]:
        """Get active internship for a user (if any)."""
        internships = await self.repo.get_by_user(user_id, InternshipStatus.ACTIVE)
        return internships[0] if internships else None

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        status: Optional[InternshipStatus] = None,
    ) -> tuple[Sequence[Internship], int]:
        """Get all internships (for admin)."""
        return await self.repo.get_all(offset, limit, status)

    async def create_from_application(
        self,
        data: InternshipCreate,
    ) -> Internship:
        """Create internship after application approval."""
        # Verify application exists and is approved
        application = await self.application_repo.get_by_id(data.application_id)
        if not application:
            raise InternshipError("Application not found")
        if application.status != ApplicationStatus.APPROVED:
            raise InternshipError("Application must be approved first")

        # Check if internship already exists for this application
        existing = await self.repo.get_by_application(data.application_id)
        if existing:
            raise InternshipError("Internship already exists for this application")

        # Validate dates
        if data.expected_end_date <= data.start_date:
            raise InternshipError("End date must be after start date")

        return await self.repo.create(
            application_id=data.application_id,
            start_date=data.start_date,
            expected_end_date=data.expected_end_date,
            supervisor_name=data.supervisor_name,
            supervisor_email=data.supervisor_email,
            supervisor_phone=data.supervisor_phone,
        )

    async def complete(
        self,
        internship_id: int,
        data: InternshipComplete,
    ) -> Internship:
        """Complete an internship."""
        internship = await self.repo.get_by_id(internship_id)
        if not internship:
            raise InternshipError("Internship not found")
        if internship.status != InternshipStatus.ACTIVE:
            raise InternshipError("Can only complete active internships")

        return await self.repo.complete(
            internship,
            data.actual_end_date,
            data.final_grade,
            data.total_hours,
        )

    async def cancel(self, internship_id: int, reason: str = "") -> Internship:
        """Cancel an internship."""
        internship = await self.repo.get_by_id(internship_id)
        if not internship:
            raise InternshipError("Internship not found")
        if internship.status != InternshipStatus.ACTIVE:
            raise InternshipError("Can only cancel active internships")

        return await self.repo.update(internship, status=InternshipStatus.CANCELLED)

    # Report operations
    async def create_report(
        self,
        user_id: int,
        data: ReportCreate,
    ) -> InternshipReport:
        """Create a new monthly report."""
        internship = await self.repo.get_by_id(data.internship_id)
        if not internship:
            raise InternshipError("Internship not found")

        # Verify user owns this internship
        if internship.application.user_id != user_id:
            raise InternshipError("You can only create reports for your own internship")

        if internship.status != InternshipStatus.ACTIVE:
            raise InternshipError("Can only add reports to active internships")

        # Check for duplicate month
        existing_reports = await self.repo.get_reports_by_internship(data.internship_id)
        for report in existing_reports:
            if report.month_number == data.month_number:
                raise InternshipError(f"Report for month {data.month_number} already exists")

        return await self.repo.create_report(
            internship_id=data.internship_id,
            month_number=data.month_number,
            report_date=data.report_date,
            hours_worked=data.hours_worked,
            activities_summary=data.activities_summary,
            achievements=data.achievements,
            challenges=data.challenges,
        )

    async def submit_report(self, report_id: int, user_id: int) -> InternshipReport:
        """Submit a report for review."""
        report = await self.repo.get_report_by_id(report_id)
        if not report:
            raise InternshipError("Report not found")

        internship = await self.repo.get_by_id(report.internship_id)
        if internship and internship.application.user_id != user_id:
            raise InternshipError("You can only submit your own reports")

        if report.status != ReportStatus.DRAFT:
            raise InternshipError("Report has already been submitted")

        return await self.repo.submit_report(report)

    async def review_report(
        self,
        report_id: int,
        reviewer_data: ReportReview,
    ) -> InternshipReport:
        """Review a submitted report."""
        report = await self.repo.get_report_by_id(report_id)
        if not report:
            raise InternshipError("Report not found")

        if report.status not in [ReportStatus.SUBMITTED, ReportStatus.REVISION_NEEDED]:
            raise InternshipError("Report is not ready for review")

        return await self.repo.review_report(
            report,
            reviewer_data.status,
            reviewer_data.supervisor_comments,
            reviewer_data.supervisor_grade,
        )

    async def get_reports(self, internship_id: int) -> Sequence[InternshipReport]:
        """Get all reports for an internship."""
        return await self.repo.get_reports_by_internship(internship_id)
