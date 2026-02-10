"""
Approve Application Use Case.
"""
from datetime import date

from app.domain.repositories.internship_repository import (
    IApplicationRepository,
    IInternshipRepository,
)
from app.domain.entities.internship.internship import Internship
from app.domain.value_objects.internship import ApplicationStatus, InternshipStatus


class ApproveApplicationUseCase:
    """Use case to approve an internship application and start the internship."""

    def __init__(
        self,
        application_repo: IApplicationRepository,
        internship_repo: IInternshipRepository,
    ):
        self.application_repo = application_repo
        self.internship_repo = internship_repo

    async def execute(
        self,
        application_id: int,
        reviewer_id: int,
        start_date: date,
        end_date: date,
        supervisor_name: str,
        supervisor_email: str,
        comments: str = "",
    ) -> Internship:
        """
        Approve application and create active internship record.
        """
        # 1. Get application
        app = await self.application_repo.get_by_id(application_id)
        if not app:
            raise ValueError("Application not found")
            
        if not app.is_pending:
            raise ValueError(f"Application is in status {app.status}, cannot approve")

        # 2. Approve application
        app.approve(reviewer_id, comments)
        await self.application_repo.update(app)

        # 3. Create Internship record
        internship = Internship(
            application_id=app.id,
            start_date=start_date,
            expected_end_date=end_date,
            supervisor_name=supervisor_name,
            supervisor_email=supervisor_email,
            status=InternshipStatus.ACTIVE
        )
        
        saved_internship = await self.internship_repo.save(internship)
        return saved_internship
