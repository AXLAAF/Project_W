"""
Approve Application Use Case.
Converts an application into an active internship.
"""
from datetime import date
from typing import Optional

from app.domain.repositories.internship_repository import (
    IApplicationRepository,
    IInternshipRepository,
    IPositionRepository,
)
from app.domain.entities.internship.internship import Internship
from app.domain.value_objects.internship import ApplicationStatus


class ApproveApplicationUseCase:
    """
    Use case: Approve an internship application.
    """
    
    def __init__(
        self,
        application_repo: IApplicationRepository,
        internship_repo: IInternshipRepository,
        position_repo: IPositionRepository,
    ):
        self.application_repo = application_repo
        self.internship_repo = internship_repo
        self.position_repo = position_repo
        
    async def execute(
        self,
        application_id: int,
        reviewer_id: int,
        start_date: date,
        expected_end_date: date,
        supervisor_name: str,
        supervisor_email: str,
        supervisor_phone: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Internship:
        # 1. Get Application
        application = await self.application_repo.get_by_id(application_id)
        if not application:
            raise ValueError(f"Application {application_id} not found")
            
        if application.status != ApplicationStatus.PENDING and application.status != ApplicationStatus.UNDER_REVIEW:
             raise ValueError(f"Application is in {application.status} status, cannot approve")

        # 2. Get Position (to decrement spots)
        position = await self.position_repo.get_by_id(application.position_id)
        if not position:
            raise ValueError("Position not found")
            
        if not position.is_available:
            raise ValueError("Position no longer has spots available")
            
        # 3. Approve Application
        application.approve(reviewer_id, notes)
        await self.application_repo.save(application)
        
        # 4. Create Active Internship
        internship = Internship.create(
            application_id=application_id,
            student_id=application.student_id,
            start_date=start_date,
            expected_end_date=expected_end_date,
            supervisor_name=supervisor_name,
            supervisor_email=supervisor_email,
            supervisor_phone=supervisor_phone,
        )
        
        # 5. Update Position Count
        position.increment_filled()
        await self.position_repo.save(position)
        
        # 6. Save Internship
        return await self.internship_repo.save(internship)
