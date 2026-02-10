"""
Unit tests for Risk domain entities and value objects.
"""
import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.domain.entities.risk.risk_assessment import RiskAssessment
from app.domain.entities.risk.attendance import Attendance, AttendanceStats
from app.domain.entities.risk.partial_grade import PartialGrade
from app.domain.entities.risk.assignment import Assignment, AssignmentSubmission, AssignmentStats
from app.domain.value_objects.risk import (
    RiskLevel,
    RiskScore,
    AttendanceStatus,
    GradeType,
    SubmissionStatus,
)


class TestRiskScore:
    """Tests for RiskScore value object."""
    
    def test_create_valid_score(self):
        """Test creating a valid risk score."""
        score = RiskScore(50)
        assert score.value == 50
        assert score.percentage == 50
    
    def test_invalid_score_below_zero(self):
        """Test that scores below 0 are rejected."""
        with pytest.raises(ValueError):
            RiskScore(-1)
    
    def test_invalid_score_above_100(self):
        """Test that scores above 100 are rejected."""
        with pytest.raises(ValueError):
            RiskScore(101)
    
    def test_risk_level_low(self):
        """Test LOW risk level for scores 0-30."""
        assert RiskScore(0).level == RiskLevel.LOW
        assert RiskScore(30).level == RiskLevel.LOW
    
    def test_risk_level_medium(self):
        """Test MEDIUM risk level for scores 31-60."""
        assert RiskScore(31).level == RiskLevel.MEDIUM
        assert RiskScore(60).level == RiskLevel.MEDIUM
    
    def test_risk_level_high(self):
        """Test HIGH risk level for scores 61-80."""
        assert RiskScore(61).level == RiskLevel.HIGH
        assert RiskScore(80).level == RiskLevel.HIGH
    
    def test_risk_level_critical(self):
        """Test CRITICAL risk level for scores 81-100."""
        assert RiskScore(81).level == RiskLevel.CRITICAL
        assert RiskScore(100).level == RiskLevel.CRITICAL
    
    def test_is_at_risk(self):
        """Test is_at_risk property."""
        assert not RiskScore(30).is_at_risk
        assert not RiskScore(60).is_at_risk
        assert RiskScore(61).is_at_risk
        assert RiskScore(85).is_at_risk


class TestRiskAssessment:
    """Tests for RiskAssessment entity."""
    
    def test_create_assessment(self):
        """Test creating a risk assessment."""
        assessment = RiskAssessment.create(
            student_id=1,
            group_id=10,
            attendance_score=30,
            grades_score=40,
            assignments_score=20,
        )
        # Expected: 30*0.3 + 40*0.4 + 20*0.3 = 9 + 16 + 6 = 31
        assert assessment.score_value == 31
        assert assessment.risk_level == RiskLevel.MEDIUM
    
    def test_is_at_risk(self):
        """Test is_at_risk property."""
        low_risk = RiskAssessment.create(1, 10, 10, 10, 10)
        high_risk = RiskAssessment.create(1, 10, 80, 80, 80)
        
        assert not low_risk.is_at_risk
        assert high_risk.is_at_risk
    
    def test_main_risk_factor(self):
        """Test determining main risk factor."""
        assessment = RiskAssessment(
            student_id=1,
            group_id=10,
            risk_score=50,
            attendance_score=80,
            grades_score=40,
            assignments_score=30,
        )
        from app.domain.value_objects.risk import RiskFactor
        assert assessment.main_risk_factor == RiskFactor.ATTENDANCE


class TestAttendance:
    """Tests for Attendance entity."""
    
    def test_create_attendance(self):
        """Test creating an attendance record."""
        attendance = Attendance.record(
            student_id=1,
            group_id=10,
            class_date=date.today(),
            status=AttendanceStatus.PRESENT,
            recorded_by=100,
        )
        assert attendance.is_present
        assert not attendance.is_absence
    
    def test_is_absence(self):
        """Test absence detection."""
        attendance = Attendance(
            student_id=1,
            group_id=10,
            class_date=date.today(),
            status=AttendanceStatus.ABSENT,
        )
        assert attendance.is_absence
        assert not attendance.is_present
    
    def test_late_counts_as_present(self):
        """Test that late counts as present."""
        attendance = Attendance(
            student_id=1,
            group_id=10,
            class_date=date.today(),
            status=AttendanceStatus.LATE,
        )
        assert attendance.is_present
        assert not attendance.is_absence


class TestAttendanceStats:
    """Tests for AttendanceStats aggregate."""
    
    def test_attendance_rate_calculation(self):
        """Test attendance rate calculation."""
        stats = AttendanceStats(
            total_classes=10,
            present=7,
            late=1,
            absent=2,
        )
        # Present + Late = 8 out of 10 = 80%
        assert stats.attendance_rate == 80.0
    
    def test_empty_stats(self):
        """Test stats with no classes."""
        stats = AttendanceStats()
        assert stats.attendance_rate == 100.0
        assert stats.absence_rate == 0.0


class TestPartialGrade:
    """Tests for PartialGrade entity."""
    
    def test_create_grade(self):
        """Test creating a grade."""
        grade = PartialGrade.record(
            student_id=1,
            group_id=10,
            grade_type=GradeType.EXAM,
            name="Examen 1",
            grade=8.5,
            recorded_by=100,
        )
        assert grade.normalized_grade == 8.5
        assert grade.is_passing
    
    def test_normalized_grade_different_scale(self):
        """Test grade normalization on 100-point scale."""
        grade = PartialGrade(
            student_id=1,
            group_id=10,
            grade_type=GradeType.EXAM,
            name="Test",
            grade=Decimal("85"),
            max_grade=Decimal("100"),
            graded_at=datetime.now(),
        )
        assert grade.normalized_grade == 8.5
    
    def test_is_passing(self):
        """Test passing grade detection."""
        passing = PartialGrade(
            student_id=1, group_id=10, grade_type=GradeType.QUIZ,
            name="Q1", grade=Decimal("6.0"), graded_at=datetime.now(),
        )
        failing = PartialGrade(
            student_id=1, group_id=10, grade_type=GradeType.QUIZ,
            name="Q2", grade=Decimal("5.9"), graded_at=datetime.now(),
        )
        
        assert passing.is_passing
        assert not failing.is_passing
    
    def test_letter_grade(self):
        """Test letter grade conversion."""
        grade = PartialGrade(
            student_id=1, group_id=10, grade_type=GradeType.EXAM,
            name="E1", grade=Decimal("8.5"), graded_at=datetime.now(),
        )
        assert grade.letter_grade == "A-"


class TestAssignment:
    """Tests for Assignment entity."""
    
    def test_create_assignment(self):
        """Test creating an assignment."""
        due = datetime.now() + timedelta(days=7)
        assignment = Assignment.create(
            group_id=10,
            title="Homework 1",
            due_date=due,
            created_by=100,
        )
        assert assignment.title == "Homework 1"
        assert not assignment.is_past_due
    
    def test_is_past_due(self):
        """Test past due detection."""
        past = datetime.now() - timedelta(days=1)
        assignment = Assignment(
            group_id=10,
            title="Old HW",
            due_date=past,
        )
        assert assignment.is_past_due
    
    def test_late_penalty_calculation(self):
        """Test late penalty calculation."""
        assignment = Assignment(
            group_id=10,
            title="HW",
            due_date=datetime.now(),
            late_penalty_percent=10.0,
        )
        assert assignment.calculate_late_penalty(3) == 30.0
        assert assignment.calculate_late_penalty(15) == 100.0  # Max 100%


class TestAssignmentSubmission:
    """Tests for AssignmentSubmission entity."""
    
    def test_create_submission(self):
        """Test creating a submission."""
        submission = AssignmentSubmission.create(
            assignment_id=1,
            student_id=100,
        )
        assert submission.status == SubmissionStatus.PENDING
        assert not submission.is_submitted
    
    def test_submit_assignment(self):
        """Test submitting an assignment."""
        submission = AssignmentSubmission(
            assignment_id=1,
            student_id=100,
            status=SubmissionStatus.PENDING,
        )
        submission.submit(file_url="http://example.com/file.pdf")
        
        assert submission.is_submitted
        assert submission.status == SubmissionStatus.SUBMITTED
    
    def test_grade_submission(self):
        """Test grading a submission."""
        submission = AssignmentSubmission(
            assignment_id=1,
            student_id=100,
            status=SubmissionStatus.SUBMITTED,
            submitted_at=datetime.now(),
        )
        submission.grade(score=85.0, graded_by=100, feedback="Good work!")
        
        assert submission.is_graded
        assert submission.score == 85.0
        assert submission.feedback == "Good work!"


class TestAssignmentStats:
    """Tests for AssignmentStats aggregate."""
    
    def test_on_time_rate(self):
        """Test on-time rate calculation."""
        stats = AssignmentStats(
            total_assignments=10,
            submitted=8,
            late=2,
            missing=2,
        )
        # On-time = 8 - 2 = 6 out of 10 = 60%
        assert stats.on_time_rate == 60.0
    
    def test_completion_rate(self):
        """Test completion rate calculation."""
        stats = AssignmentStats(
            total_assignments=10,
            submitted=7,
            missing=3,
        )
        assert stats.completion_rate == 70.0
