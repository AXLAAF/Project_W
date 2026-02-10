"""
Unit tests for RiskScoreCalculator domain service.
"""
import pytest

from app.domain.services.risk_score_calculator import (
    RiskScoreCalculator,
    RiskWeights,
    RiskThresholds,
)
from app.domain.entities.risk.attendance import AttendanceStats
from app.domain.entities.risk.assignment import AssignmentStats
from app.domain.value_objects.risk import RiskLevel


class TestRiskScoreCalculator:
    """Tests for RiskScoreCalculator domain service."""
    
    @pytest.fixture
    def calculator(self):
        """Create calculator with default weights."""
        return RiskScoreCalculator()
    
    # ============ Attendance Risk Tests ============
    
    def test_attendance_risk_excellent(self, calculator):
        """Test attendance risk for excellent attendance (>=95%)."""
        stats = AttendanceStats(total_classes=20, present=19, late=1)
        assert calculator.calculate_attendance_risk(stats) == 0
    
    def test_attendance_risk_good(self, calculator):
        """Test attendance risk for good attendance (90-94%)."""
        stats = AttendanceStats(total_classes=20, present=18)
        assert calculator.calculate_attendance_risk(stats) == 10
    
    def test_attendance_risk_moderate(self, calculator):
        """Test attendance risk for moderate attendance (80-84%)."""
        stats = AttendanceStats(total_classes=20, present=16)
        assert calculator.calculate_attendance_risk(stats) == 40
    
    def test_attendance_risk_critical(self, calculator):
        """Test attendance risk for critical attendance (<70%)."""
        stats = AttendanceStats(total_classes=20, present=12, absent=8)
        assert calculator.calculate_attendance_risk(stats) == 100
    
    # ============ Grades Risk Tests ============
    
    def test_grades_risk_excellent(self, calculator):
        """Test grades risk for excellent average (>=9.0)."""
        assert calculator.calculate_grades_risk(9.5) == 0
    
    def test_grades_risk_good(self, calculator):
        """Test grades risk for good average (8.0-8.9)."""
        assert calculator.calculate_grades_risk(8.5) == 10
    
    def test_grades_risk_at_risk(self, calculator):
        """Test grades risk for at-risk average (6.0-6.4)."""
        assert calculator.calculate_grades_risk(6.0) == 55
    
    def test_grades_risk_failing(self, calculator):
        """Test grades risk for failing average (<5.0)."""
        assert calculator.calculate_grades_risk(4.0) == 100
    
    def test_grades_risk_no_grades(self, calculator):
        """Test grades risk when no grades exist."""
        assert calculator.calculate_grades_risk(0) == 50
    
    # ============ Assignments Risk Tests ============
    
    def test_assignments_risk_excellent(self, calculator):
        """Test assignments risk for excellent submission rate."""
        stats = AssignmentStats(total_assignments=10, submitted=10, late=0)
        assert calculator.calculate_assignments_risk(stats) == 0
    
    def test_assignments_risk_many_missing(self, calculator):
        """Test assignments risk with >50% missing."""
        stats = AssignmentStats(total_assignments=10, submitted=4, missing=6)
        assert calculator.calculate_assignments_risk(stats) == 100
    
    def test_assignments_risk_no_assignments(self, calculator):
        """Test assignments risk when no assignments exist."""
        stats = AssignmentStats()
        assert calculator.calculate_assignments_risk(stats) == 0
    
    # ============ Total Score Tests ============
    
    def test_total_score_calculation(self, calculator):
        """Test weighted total score calculation."""
        score = calculator.calculate_total_score(
            attendance_score=30,  # 30 * 0.3 = 9
            grades_score=40,      # 40 * 0.4 = 16
            assignments_score=20, # 20 * 0.3 = 6
        )
        assert score.value == 31
    
    def test_total_score_capped_at_100(self, calculator):
        """Test that total score is capped at 100."""
        score = calculator.calculate_total_score(100, 100, 100)
        assert score.value == 100
    
    # ============ Full Assessment Tests ============
    
    def test_assess_low_risk_student(self, calculator):
        """Test assessment for a low-risk student."""
        assessment = calculator.assess(
            student_id=1,
            group_id=10,
            attendance_stats=AttendanceStats(total_classes=20, present=19, late=1),
            grade_average=9.0,
            assignment_stats=AssignmentStats(total_assignments=10, submitted=10),
        )
        assert assessment.risk_level == RiskLevel.LOW
        assert not assessment.is_at_risk
    
    def test_assess_critical_risk_student(self, calculator):
        """Test assessment for a critical-risk student."""
        assessment = calculator.assess(
            student_id=1,
            group_id=10,
            attendance_stats=AttendanceStats(total_classes=20, present=10, absent=10),
            grade_average=4.5,
            assignment_stats=AssignmentStats(total_assignments=10, submitted=3, missing=7),
        )
        assert assessment.risk_level == RiskLevel.CRITICAL
        assert assessment.is_at_risk
        assert assessment.needs_intervention()
    
    def test_recommendation_for_critical(self, calculator):
        """Test recommendations are generated for critical risk."""
        assessment = calculator.assess(
            student_id=1,
            group_id=10,
            attendance_stats=AttendanceStats(total_classes=20, present=10, absent=10),
            grade_average=4.5,
            assignment_stats=AssignmentStats(total_assignments=10, submitted=3, missing=7),
        )
        assert "CRÍTICO" in assessment.recommendation
        assert "intervención" in assessment.recommendation.lower()


class TestRiskWeights:
    """Tests for RiskWeights configuration."""
    
    def test_valid_weights(self):
        """Test creating valid weights."""
        weights = RiskWeights(attendance=0.25, grades=0.50, assignments=0.25)
        assert weights.attendance == 0.25
    
    def test_invalid_weights_sum(self):
        """Test that weights must sum to 1.0."""
        with pytest.raises(ValueError):
            RiskWeights(attendance=0.3, grades=0.3, assignments=0.3)


class TestCustomWeights:
    """Tests for calculator with custom weights."""
    
    def test_grades_heavy_weight(self):
        """Test calculator with heavier grade weight."""
        calculator = RiskScoreCalculator(
            weights=RiskWeights(attendance=0.2, grades=0.6, assignments=0.2)
        )
        # With same scores, higher grades weight should increase impact
        score = calculator.calculate_total_score(
            attendance_score=0,
            grades_score=100,
            assignments_score=0,
        )
        assert score.value == 60  # 100 * 0.6
