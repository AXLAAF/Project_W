"""
Unit tests for Planning infrastructure adapters (mappers).
Tests mapping between domain entities and SQLAlchemy ORM models.
"""
import pytest
from datetime import time, datetime
from decimal import Decimal
from unittest.mock import MagicMock

from app.infrastructure.persistence.sqlalchemy.planning_mappers import (
    SubjectMapper,
    SubjectPrerequisiteMapper,
    GroupMapper,
    ScheduleMapper,
    EnrollmentMapper,
)
from app.domain.entities.planning.subject import Subject as SubjectEntity, Prerequisite
from app.domain.entities.planning.group import Group as GroupEntity, Schedule as ScheduleEntity, DayOfWeek
from app.domain.entities.planning.enrollment import Enrollment as EnrollmentEntity, EnrollmentStatus
from app.domain.value_objects.planning import SubjectCode, Credits, Grade


class TestSubjectMapper:
    """Tests for SubjectMapper."""
    
    def test_to_entity_converts_basic_fields(self):
        """Test ORM model to domain entity conversion."""
        # Create mock ORM model
        model = MagicMock()
        model.id = 1
        model.code = "MAT101"
        model.name = "Mathematics I"
        model.credits = 4
        model.hours_theory = 3
        model.hours_practice = 1
        model.hours_lab = 0
        model.description = "Basic math"
        model.department = "Mathematics"
        model.semester_suggested = 1
        model.is_active = True
        model.prerequisites = []
        model.created_at = datetime(2024, 1, 1)
        model.updated_at = datetime(2024, 1, 2)
        
        entity = SubjectMapper.to_entity(model)
        
        assert entity.id == 1
        assert entity.code_str == "MAT101"
        assert entity.name == "Mathematics I"
        assert entity.credits_value == 4
        assert entity.hours_theory == 3
        assert entity.hours_practice == 1
        assert entity.hours_lab == 0
        assert entity.description == "Basic math"
        assert entity.department == "Mathematics"
        assert entity.semester_suggested == 1
        assert entity.is_active is True
    
    def test_to_entity_with_prerequisites(self):
        """Test conversion with prerequisites."""
        prereq_model = MagicMock()
        prereq_model.prerequisite_id = 2
        prereq_model.prerequisite.code = "PRE101"
        prereq_model.prerequisite.name = "Prerequisites"
        prereq_model.is_mandatory = True
        
        model = MagicMock()
        model.id = 1
        model.code = "MAT201"
        model.name = "Mathematics II"
        model.credits = 4
        model.hours_theory = 3
        model.hours_practice = 0
        model.hours_lab = 0
        model.description = None
        model.department = "Mathematics"
        model.semester_suggested = 2
        model.is_active = True
        model.prerequisites = [prereq_model]
        model.created_at = datetime(2024, 1, 1)
        model.updated_at = None
        
        entity = SubjectMapper.to_entity(model)
        
        assert len(entity.prerequisites) == 1
        assert entity.prerequisites[0].prerequisite_subject_id == 2
        assert entity.prerequisites[0].prerequisite_code == "PRE101"
    
    def test_to_model_converts_entity(self):
        """Test domain entity to ORM model conversion."""
        entity = SubjectEntity(
            code=SubjectCode("MAT101"),
            name="Mathematics I",
            credits=Credits(4),
            hours_theory=3,
            hours_practice=1,
            hours_lab=0,
            description="Basic math",
            department="Mathematics",
            semester_suggested=1,
            is_active=True,
        )
        
        model = SubjectMapper.to_model(entity)
        
        assert model.code == "MAT101"
        assert model.name == "Mathematics I"
        assert model.credits == 4
        assert model.hours_theory == 3
    
    def test_to_model_includes_id_when_present(self):
        """Test that ID is included when entity has one."""
        entity = SubjectEntity(
            id=42,
            code=SubjectCode("MAT101"),
            name="Mathematics I",
            credits=Credits(4),
        )
        
        model = SubjectMapper.to_model(entity)
        
        assert model.id == 42


class TestScheduleMapper:
    """Tests for ScheduleMapper."""
    
    def test_to_entity_converts_schedule(self):
        """Test ORM model to Schedule entity conversion."""
        model = MagicMock()
        model.id = 1
        model.group_id = 10
        model.day_of_week = 1  # Monday
        model.start_time = time(8, 0)
        model.end_time = time(10, 0)
        model.classroom = "A101"
        model.schedule_type = "class"
        
        entity = ScheduleMapper.to_entity(model)
        
        assert entity.day_of_week == DayOfWeek.MONDAY
        assert entity.start_time == time(8, 0)
        assert entity.end_time == time(10, 0)
        assert entity.classroom == "A101"
        assert entity.id == 1
        assert entity.group_id == 10
    
    def test_orm_day_to_domain_mapping(self):
        """Test day of week conversion ORM -> Domain."""
        assert ScheduleMapper._orm_day_to_domain(1) == DayOfWeek.MONDAY
        assert ScheduleMapper._orm_day_to_domain(5) == DayOfWeek.FRIDAY
        assert ScheduleMapper._orm_day_to_domain(7) == DayOfWeek.SUNDAY
    
    def test_domain_day_to_orm_mapping(self):
        """Test day of week conversion Domain -> ORM."""
        assert ScheduleMapper._domain_day_to_orm(DayOfWeek.MONDAY) == 1
        assert ScheduleMapper._domain_day_to_orm(DayOfWeek.FRIDAY) == 5
        assert ScheduleMapper._domain_day_to_orm(DayOfWeek.SUNDAY) == 7


class TestGroupMapper:
    """Tests for GroupMapper."""
    
    def test_to_entity_converts_basic_fields(self):
        """Test ORM model to Group entity conversion."""
        model = MagicMock()
        model.id = 1
        model.subject_id = 10
        model.period_id = 5
        model.group_number = "001"
        model.professor_id = 20
        model.professor = None  # No professor relationship
        model.capacity = 30
        model.enrolled_count = 15
        model.classroom = "A101"
        model.modality = "presencial"
        model.is_active = True
        model.subject = MagicMock()
        model.subject.code = "MAT101"
        model.subject.name = "Math I"
        model.period = MagicMock()
        model.period.name = "2024-1"
        model.schedules = []
        model.created_at = datetime(2024, 1, 1)
        
        entity = GroupMapper.to_entity(model)
        
        assert entity.id == 1
        assert entity.subject_id == 10
        assert entity.period_id == 5
        assert entity.group_number == "001"
        assert entity.capacity == 30
        assert entity.enrolled_count == 15
        assert entity.subject_code == "MAT101"
        assert entity.modality == "presencial"
    
    def test_to_entity_with_schedules(self):
        """Test conversion with schedules."""
        schedule_model = MagicMock()
        schedule_model.id = 1
        schedule_model.group_id = 1
        schedule_model.day_of_week = 1
        schedule_model.start_time = time(8, 0)
        schedule_model.end_time = time(10, 0)
        schedule_model.classroom = "A101"
        schedule_model.schedule_type = "class"
        
        model = MagicMock()
        model.id = 1
        model.subject_id = 10
        model.period_id = 5
        model.group_number = "001"
        model.professor_id = None
        model.professor = None
        model.capacity = 30
        model.enrolled_count = 0
        model.classroom = "A101"
        model.modality = "presencial"
        model.is_active = True
        model.subject = None
        model.period = None
        model.schedules = [schedule_model]
        model.created_at = datetime(2024, 1, 1)
        
        entity = GroupMapper.to_entity(model)
        
        assert len(entity.schedules) == 1
        assert entity.schedules[0].day_of_week == DayOfWeek.MONDAY


class TestEnrollmentMapper:
    """Tests for EnrollmentMapper."""
    
    def test_to_entity_converts_basic_enrollment(self):
        """Test ORM model to Enrollment entity conversion."""
        model = MagicMock()
        model.id = 1
        model.student_id = 100
        model.group_id = 10
        model.status = "ENROLLED"
        model.grade = None
        model.attempt_number = 1
        model.enrolled_at = datetime(2024, 1, 15)
        model.completed_at = None
        model.created_at = datetime(2024, 1, 15)
        model.updated_at = datetime(2024, 1, 15)
        model.group = MagicMock()
        model.group.subject = MagicMock()
        model.group.subject.code = "MAT101"
        model.group.subject.name = "Math I"
        
        entity = EnrollmentMapper.to_entity(model)
        
        assert entity.id == 1
        assert entity.student_id == 100
        assert entity.group_id == 10
        assert entity.status == EnrollmentStatus.ENROLLED
        assert entity.grade is None
        assert entity.subject_code == "MAT101"
    
    def test_to_entity_with_grade(self):
        """Test conversion with grade."""
        model = MagicMock()
        model.id = 1
        model.student_id = 100
        model.group_id = 10
        model.status = "PASSED"
        model.grade = Decimal("8.5")
        model.attempt_number = 1
        model.enrolled_at = datetime(2024, 1, 15)
        model.completed_at = datetime(2024, 5, 15)
        model.created_at = datetime(2024, 1, 15)
        model.updated_at = datetime(2024, 5, 15)
        model.group = MagicMock()
        model.group.subject = MagicMock()
        model.group.subject.code = "MAT101"
        model.group.subject.name = "Math I"
        
        entity = EnrollmentMapper.to_entity(model)
        
        assert entity.status == EnrollmentStatus.PASSED
        assert entity.grade is not None
        assert entity.grade.value == Decimal("8.5")
        assert entity.grade.letter == "B"
    
    def test_status_mapping_all_statuses(self):
        """Test all enrollment status mappings."""
        assert EnrollmentMapper._orm_status_to_domain("ENROLLED") == EnrollmentStatus.ENROLLED
        assert EnrollmentMapper._orm_status_to_domain("PASSED") == EnrollmentStatus.PASSED
        assert EnrollmentMapper._orm_status_to_domain("FAILED") == EnrollmentStatus.FAILED
        assert EnrollmentMapper._orm_status_to_domain("DROPPED") == EnrollmentStatus.DROPPED
        assert EnrollmentMapper._orm_status_to_domain("WITHDRAWN") == EnrollmentStatus.WITHDRAWN
        assert EnrollmentMapper._orm_status_to_domain("PENDING") == EnrollmentStatus.PENDING
    
    def test_to_model_converts_entity(self):
        """Test domain entity to ORM model conversion."""
        entity = EnrollmentEntity(
            student_id=100,
            group_id=10,
            status=EnrollmentStatus.ENROLLED,
            attempt_number=1,
            enrolled_at=datetime(2024, 1, 15),
        )
        
        model = EnrollmentMapper.to_model(entity)
        
        assert model.student_id == 100
        assert model.group_id == 10
        assert model.status == "ENROLLED"
        assert model.attempt_number == 1
