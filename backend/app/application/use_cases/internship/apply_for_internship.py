"""
Apply for Internship Use Case.
"""
from datetime import datetime
from typing import Optional

from app.domain.repositories.internship_repository import (
    IApplicationRepository,
    IPositionRepository,
)
from app.domain.entities.internship.application import InternshipApplication
from app.domain.entities.internship.position import InternshipPosition
from app.domain.value_objects.internship import ApplicationStatus


class ApplyForInternshipUseCase:
    """Use case for students to apply for an internship position."""

    def __init__(
        self,
        application_repo: IApplicationRepository,
        position_repo: IPositionRepository,
    ):
        self.application_repo = application_repo
        self.position_repo = position_repo

    async def execute(
        self,
        student_id: int,
        position_id: int,
        cv_url: Optional[str] = None,
        cover_letter: Optional[str] = None,
    ) -> InternshipApplication:
        """
        Submit an application for a position.
        
        Raises:
            ValueError: If position not found, not open, or already applied.
        """
        # 1. Check if position exists and is open
        position = await self.position_repo.get_by_id(position_id)
        if not position:
            raise ValueError("Position not found")
        
        if not position.is_open:
            raise ValueError("Position is not open for applications")

        # 2. Check if already applied
        existing = await self.application_repo.get_by_student_and_position(
            student_id, position_id
        )
        if existing:
            raise ValueError("You have already applied for this position")

        # 3. Create application
        application = InternshipApplication(
            student_id=student_id,
            position_id=position_id,
            cv_url=cv_url,
            cover_letter=cover_letter,
            status=ApplicationStatus.PENDING,
        )

        # 4. Save
        saved_app = await self.application_repo.save(application)
        return saved_app
