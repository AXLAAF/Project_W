"""
Tests for Risk module use cases.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from app.application.use_cases.calculate_risk import CalculateRiskScoreUseCase
from app.application.use_cases.get_risk_factors import GetRiskFactorsUseCase
from app.domain.entities.risk.risk_assessment import RiskAssessment
from app.domain.value_objects.risk import RiskScore, RiskLevel
from app.domain.entities.risk.attendance import AttendanceStats


class TestRiskUseCases:
    
    @pytest.mark.asyncio
    async def test_calculate_risk_score(self):
        """Test standard risk calculation flow."""
        # Mocks
        risk_repo = AsyncMock()
        att_repo = AsyncMock()
        grade_repo = AsyncMock()
        assign_repo = AsyncMock()
        risk_model = AsyncMock()
        
        # Setup Data
        att_stats = AttendanceStats(total_classes=20, present=18, absent=2)
        att_repo.get_stats.return_value = att_stats
        
        grade_repo.get_average.return_value = 8.5
        
        assign_stats = MagicMock()
        assign_stats.submission_rate = 95.0
        assign_repo.get_submission_stats.return_value = assign_stats
        
        # Model returns low risk (15)
        risk_model.predict_risk.return_value = RiskScore(15)
        risk_model.analyze_factors.return_value = [{"factor": "None", "weight": 0}]
        
        # Capture the saved object
        async def save_side_effect(assessment):
            return assessment
        risk_repo.save.side_effect = save_side_effect
        
        use_case = CalculateRiskScoreUseCase(
            risk_repo, att_repo, grade_repo, assign_repo, risk_model
        )
        
        # Execute
        result = await use_case.execute(student_id=1, group_id=101)
        
        # Assert
        assert isinstance(result, RiskAssessment)
        assert result.risk_score.value == 15
        assert result.risk_level == RiskLevel.LOW
        # 100 - 90 = 10 risk points for attendance
        assert result.attendance_score <= 10 
        
        att_repo.get_stats.assert_called_once()
        risk_model.predict_risk.assert_called_once()
        risk_repo.save.assert_called_once()


    @pytest.mark.asyncio
    async def test_get_risk_factors(self):
        """Test retrieving risk factors."""
        risk_repo = AsyncMock()
        
        # Mock existing assessment (High Risk 75)
        assessment = RiskAssessment(
            student_id=1,
            group_id=101,
            risk_score=RiskScore(75),
            attendance_score=80,
            grades_score=60,
            assignments_score=50,
            factor_details={"factors": [{"name": "Attendance", "score": 80}]},
            recommendation="Intervene immediately",
            assessed_at=datetime.now()
        )
        risk_repo.get_latest.return_value = assessment
        
        use_case = GetRiskFactorsUseCase(risk_repo)
        
        result = await use_case.execute(student_id=1, group_id=101)
        
        assert result["has_data"] is True
        assert result["risk_level"] == "HIGH"
        assert result["risk_score"] == 75
        assert len(result["factors"]) == 1
        assert result["recommendation"] == "Intervene immediately"
