"""
Unit tests for Risk module mappers.
"""
import pytest
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import MagicMock

from app.infrastructure.persistence.sqlalchemy.risk_mappers import (
    RiskAssessmentMapper,
    AttendanceMapper,
    PartialGradeMapper,
    AssignmentMapper,
    AssignmentSubmissionMapper,
)
from app.domain.value_objects.risk import (
    RiskScore,
    RiskLevel,
    AttendanceStatus,
    GradeType,
    SubmissionStatus,
)


class TestRiskAssessmentMapper:
    """Tests for RiskAssessmentMapper."""
    
    def test_to_entity(self):
        """Test converting ORM model to domain entity."""
        model = MagicMock()
        model.id = 1
        model.student_id = 100
        model.group_id = 10
        model.risk_score = 45
        model.risk_level = "MEDIUM"
        model.attendance_score = 30
        model.grades_score = 50
        model.assignments_score = 40
        model.factor_details = {"attendance": {"score": 30}}
        model.recommendation = "Monitor closely"
        model.assessed_at = datetime(2024, 1, 15, 10, 0)
        model.created_at = datetime(2024, 1, 15, 10, 0)
        
        entity = RiskAssessmentMapper.to_entity(model)
        
        assert entity.id == 1
        assert entity.student_id == 100
        assert entity.group_id == 10
        assert entity.risk_score.value == 45
        assert entity.risk_level == RiskLevel.MEDIUM
        assert entity.attendance_score == 30
    
    def test_to_model(self):
        """Test converting domain entity to ORM model."""
        from app.domain.entities.risk.risk_assessment import RiskAssessment
        
        entity = RiskAssessment(
            id=1,
            student_id=100,
            group_id=10,
            risk_score=RiskScore(45),
            attendance_score=30,
            grades_score=50,
            assignments_score=40,
            recommendation="Test",
            assessed_at=datetime(2024, 1, 15, 10, 0),
        )
        
        model = RiskAssessmentMapper.to_model(entity)
        
        assert model.student_id == 100
        assert model.risk_score == 45
        assert model.risk_level == "MEDIUM"


class TestAttendanceMapper:
    """Tests for AttendanceMapper."""
    
    def test_to_entity(self):
        """Test converting ORM model to domain entity."""
        model = MagicMock()
        model.id = 1
        model.student_id = 100
        model.group_id = 10
        model.class_date = date(2024, 1, 15)
        model.status = "PRESENT"
        model.notes = None
        model.recorded_by = 50
        model.created_at = datetime(2024, 1, 15, 10, 0)
        
        entity = AttendanceMapper.to_entity(model)
        
        assert entity.id == 1
        assert entity.student_id == 100
        assert entity.status == AttendanceStatus.PRESENT
        assert entity.is_present
    
    def test_to_model(self):
        """Test converting domain entity to ORM model."""
        from app.domain.entities.risk.attendance import Attendance
        
        entity = Attendance(
            student_id=100,
            group_id=10,
            class_date=date(2024, 1, 15),
            status=AttendanceStatus.ABSENT,
            recorded_by=50,
        )
        
        model = AttendanceMapper.to_model(entity)
        
        assert model.student_id == 100
        assert model.status == "ABSENT"
    
    def test_update_model(self):
        """Test updating ORM model from entity."""
        from app.domain.entities.risk.attendance import Attendance
        
        model = MagicMock()
        entity = Attendance(
            student_id=100,
            group_id=10,
            class_date=date(2024, 1, 15),
            status=AttendanceStatus.EXCUSED,
            notes="Doctor's note",
            recorded_by=50,
        )
        
        AttendanceMapper.update_model(model, entity)
        
        assert model.status == "EXCUSED"
        assert model.notes == "Doctor's note"


class TestPartialGradeMapper:
    """Tests for PartialGradeMapper."""
    
    def test_to_entity(self):
        """Test converting ORM model to domain entity."""
        model = MagicMock()
        model.id = 1
        model.student_id = 100
        model.group_id = 10
        model.grade_type = "EXAM"
        model.name = "Examen 1"
        model.grade = 8.5
        model.max_grade = 10.0
        model.weight = 1.0
        model.feedback = "Good job"
        model.graded_at = datetime(2024, 1, 15, 10, 0)
        model.recorded_by = 50
        model.created_at = datetime(2024, 1, 15, 10, 0)
        
        entity = PartialGradeMapper.to_entity(model)
        
        assert entity.id == 1
        assert entity.grade == Decimal("8.5")
        assert entity.grade_type == GradeType.EXAM
        assert entity.is_passing
    
    def test_to_model(self):
        """Test converting domain entity to ORM model."""
        from app.domain.entities.risk.partial_grade import PartialGrade
        
        entity = PartialGrade(
            student_id=100,
            group_id=10,
            grade_type=GradeType.QUIZ,
            name="Quiz 1",
            grade=Decimal("7.5"),
            graded_at=datetime(2024, 1, 15, 10, 0),
            recorded_by=50,
        )
        
        model = PartialGradeMapper.to_model(entity)
        
        assert model.student_id == 100
        assert model.grade_type == "QUIZ"
        assert model.grade == Decimal("7.5")


class TestAssignmentMapper:
    """Tests for AssignmentMapper."""
    
    def test_to_entity(self):
        """Test converting ORM model to domain entity."""
        model = MagicMock()
        model.id = 1
        model.group_id = 10
        model.title = "Homework 1"
        model.description = "Complete exercises"
        model.due_date = datetime(2024, 1, 20, 23, 59)
        model.max_score = 100.0
        model.weight = 1.0
        model.allows_late = True
        model.late_penalty_percent = 10.0
        model.created_by = 50
        model.created_at = datetime(2024, 1, 15, 10, 0)
        
        entity = AssignmentMapper.to_entity(model)
        
        assert entity.id == 1
        assert entity.title == "Homework 1"
        assert entity.max_score == 100.0
        assert entity.allows_late
    
    def test_to_model(self):
        """Test converting domain entity to ORM model."""
        from app.domain.entities.risk.assignment import Assignment
        
        entity = Assignment(
            group_id=10,
            title="Project",
            due_date=datetime(2024, 2, 1, 23, 59),
            created_by=50,
        )
        
        model = AssignmentMapper.to_model(entity)
        
        assert model.group_id == 10
        assert model.title == "Project"


class TestAssignmentSubmissionMapper:
    """Tests for AssignmentSubmissionMapper."""
    
    def test_to_entity(self):
        """Test converting ORM model to domain entity."""
        model = MagicMock()
        model.id = 1
        model.assignment_id = 10
        model.student_id = 100
        model.status = "SUBMITTED"
        model.submitted_at = datetime(2024, 1, 18, 14, 30)
        model.file_url = "http://example.com/file.pdf"
        model.comments = None
        model.score = None
        model.feedback = None
        model.graded_at = None
        model.graded_by = None
        model.created_at = datetime(2024, 1, 15)
        
        entity = AssignmentSubmissionMapper.to_entity(model)
        
        assert entity.id == 1
        assert entity.status == SubmissionStatus.SUBMITTED
        assert entity.is_submitted
    
    def test_to_model(self):
        """Test converting domain entity to ORM model."""
        from app.domain.entities.risk.assignment import AssignmentSubmission
        
        entity = AssignmentSubmission(
            assignment_id=10,
            student_id=100,
            status=SubmissionStatus.GRADED,
            submitted_at=datetime(2024, 1, 18, 14, 30),
            score=85.0,
            graded_by=50,
            graded_at=datetime(2024, 1, 20, 10, 0),
        )
        
        model = AssignmentSubmissionMapper.to_model(entity)
        
        assert model.status == "GRADED"
        assert model.score == 85.0
    
    def test_update_model(self):
        """Test updating ORM model from entity."""
        from app.domain.entities.risk.assignment import AssignmentSubmission
        
        model = MagicMock()
        entity = AssignmentSubmission(
            assignment_id=10,
            student_id=100,
            status=SubmissionStatus.GRADED,
            submitted_at=datetime(2024, 1, 18),
            score=90.0,
            feedback="Excellent",
            graded_by=50,
            graded_at=datetime(2024, 1, 20),
        )
        
        AssignmentSubmissionMapper.update_model(model, entity)
        
        assert model.status == "GRADED"
        assert model.score == 90.0
        assert model.feedback == "Excellent"
