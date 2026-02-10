"""
Apply for Internship Use Case.
"""
from datetime import datetime
from typing import Optional

from app.domain.repositories.internship_repository import (
    IApplicationRepository, 
    IPositionRepository
)
from app.domain.entities.internship.application import InternshipApplication
from app.domain.entities.risk.risk_assessment import RiskAssessment # Example of cross-module check?
# Maybe check student eligibility (grades/credits) using Planning module later.


class ApplyForInternshipUseCase:
    """
    Use case: Student applies for an internship position.
    """
    
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
        cv_path: str,
        cover_letter: Optional[str] = None,
    ) -> InternshipApplication:
        # 1. Check if position exists and is available
        position = await self.position_repo.get_by_id(position_id)
        if not position:
            raise ValueError(f"Position {position_id} not found")
            
        if not position.is_available:
            raise ValueError("Position is not available (full or inactive)")
            
        # 2. Check if student already applied
        existing_apps = await self.application_repo.get_by_student(student_id)
        for app in existing_apps:
            if app.position_id == position_id:
                raise ValueError("Student already applied to this position")
        
        # 3. Create application
        application = InternshipApplication.create(
            student_id=student_id,
            position_id=position_id,
            cv_path=cv_path,
            cover_letter=cover_letter,
        )
        
        # 4. Save
        return await self.application_repo.save(application)
