"""
Submit Report Use Case.
"""
from datetime import date
from typing import Optional

from app.domain.repositories.internship_repository import (
    IInternshipRepository,
    IReportRepository,
)
from app.domain.entities.internship.report import InternshipReport
from app.domain.value_objects.internship import ReportType, ReportStatus


class SubmitReportUseCase:
    """Use case for students to submit monthly/final reports."""

    def __init__(
        self,
        internship_repo: IInternshipRepository,
        report_repo: IReportRepository,
    ):
        self.internship_repo = internship_repo
        self.report_repo = report_repo

    async def execute(
        self,
        internship_id: int,
        report_type: ReportType,
        start_date: date,
        end_date: date,
        content: str,
        hours_logged: int,
        file_url: Optional[str] = None,
    ) -> InternshipReport:
        """
        Submit a progress report.
        """
        # 1. Validate internship
        internship = await self.internship_repo.get_by_id(internship_id)
        if not internship:
            raise ValueError("Internship not found")
            
        # 2. Create report
        report = InternshipReport(
            internship_id=internship_id,
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            content=content,
            hours_logged=hours_logged,
            file_url=file_url,
            status=ReportStatus.PENDING
        )
        
        # 3. Update internship hours (optimistic update, typically verified later)
        # internship.add_hours(hours_logged)
        # await self.internship_repo.update(internship)
        
        # 4. Save report
        saved_report = await self.report_repo.save(report)
        return saved_report
