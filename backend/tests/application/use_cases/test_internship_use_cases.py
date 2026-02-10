"""
Unit tests for Internship use cases.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date

from app.application.use_cases.internship.apply_for_internship import ApplyForInternshipUseCase
from app.application.use_cases.internship.approve_application import ApproveApplicationUseCase
from app.domain.entities.internship.position import InternshipPosition
from app.domain.entities.internship.application import InternshipApplication
from app.domain.value_objects.internship import ApplicationStatus

class TestApplyForInternshipUseCase:
    @pytest.mark.asyncio
    async def test_apply_success(self):
        app_repo = AsyncMock()
        pos_repo = AsyncMock()
        
        # Position exists and is open
        pos = InternshipPosition(company_id=1, title="Dev", description="desc", requirements="Python")
        pos.id = 10
        pos_repo.get_by_id.return_value = pos
        
        # No existing application
        app_repo.get_by_student_and_position.return_value = None
        
        # Save returns the app
        async def save_side_effect(app):
            app.id = 100
            return app
        app_repo.save.side_effect = save_side_effect
        
        use_case = ApplyForInternshipUseCase(app_repo, pos_repo)
        result = await use_case.execute(student_id=1, position_id=10)
        
        assert result.student_id == 1
        assert result.position_id == 10
        assert result.status == ApplicationStatus.PENDING

    @pytest.mark.asyncio
    async def test_apply_closed_position(self):
        app_repo = AsyncMock()
        pos_repo = AsyncMock()
        
        pos = InternshipPosition(company_id=1, title="Dev", description="desc", requirements="Python", is_active=False)
        pos_repo.get_by_id.return_value = pos
        
        use_case = ApplyForInternshipUseCase(app_repo, pos_repo)
        with pytest.raises(ValueError, match="not open"):
            await use_case.execute(1, 10)

class TestApproveApplicationUseCase:
    @pytest.mark.asyncio
    async def test_approve_success(self):
        app_repo = AsyncMock()
        intern_repo = AsyncMock()
        
        # Pending application
        app = InternshipApplication(student_id=1, position_id=10)
        app.id = 100
        app_repo.get_by_id.return_value = app

        async def save_internship(internship):
            return internship
        intern_repo.save.side_effect = save_internship
        
        use_case = ApproveApplicationUseCase(app_repo, intern_repo)
        result = await use_case.execute(
            application_id=100,
            reviewer_id=5,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 1),
            supervisor_name="Boss",
            supervisor_email="boss@co.com"
        )
        
        assert app.status == ApplicationStatus.APPROVED
        assert result.status == "ACTIVE"
        assert result.application_id == 100
