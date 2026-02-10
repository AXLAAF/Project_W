"""
Unit tests for Planning domain entities.
Pure domain tests - no database, no infrastructure.
"""
import pytest
from datetime import time
from decimal import Decimal

from app.domain.entities.subject import Subject, SubjectPrerequisite
from app.domain.entities.group import Group, Schedule, DayOfWeek
from app.domain.entities.enrollment import Enrollment, EnrollmentStatus
from app.domain.value_objects.subject_code import SubjectCode
from app.domain.value_objects.credits import Credits
from app.domain.value_objects.grade import Grade


class TestSubjectEntity:
    """Test suite for Subject domain entity."""
    
    def test_create_subject_with_factory(self):
        """Test Subject.create() factory method."""
        subject = Subject.create(
            code="MAT101",
            name="Mathematics I",
            credits=4,
            department="Mathematics",
            semester_suggested=1,
        )
        
        assert subject.code_str == "MAT101"
        assert subject.name == "Mathematics I"
        assert subject.credits_value == 4
        assert subject.department == "Mathematics"
        assert subject.is_active is True
    
    def test_add_prerequisite(self):
        """Test adding prerequisites to a subject."""
        subject = Subject.create(code="MAT201", name="Math II", credits=4)
        
        subject.add_prerequisite(
            prerequisite_id=1,
            prerequisite_code="MAT101",
            prerequisite_name="Math I",
            is_mandatory=True,
        )
        
        assert len(subject.prerequisites) == 1
        assert subject.has_prerequisite("MAT101")
    
    def test_remove_prerequisite(self):
        """Test removing prerequisites."""
        subject = Subject.create(code="MAT201", name="Math II", credits=4)
        subject.add_prerequisite(1, "MAT101", "Math I")
        
        result = subject.remove_prerequisite(1)
        
        assert result is True
        assert len(subject.prerequisites) == 0
    
    def test_total_hours(self):
        """Test total hours calculation."""
        subject = Subject.create(
            code="FIS101",
            name="Physics I",
            credits=5,
            hours_theory=3,
            hours_practice=1,
            hours_lab=2,
        )
        
        assert subject.total_hours == 6


class TestGroupEntity:
    """Test suite for Group domain entity."""
    
    def test_create_group(self):
        """Test Group.create() factory method."""
        group = Group.create(
            subject_id=1,
            period_id=1,
            group_number="001",
            professor_id=10,
            capacity=30,
        )
        
        assert group.subject_id == 1
        assert group.group_number == "001"
        assert group.capacity == 30
        assert group.enrolled_count == 0
    
    def test_available_spots(self):
        """Test available spots calculation."""
        group = Group.create(subject_id=1, period_id=1, group_number="001", capacity=30)
        group.enrolled_count = 25
        
        assert group.available_spots == 5
        assert group.enrollment_percentage == pytest.approx(83.33, rel=0.1)
    
    def test_is_full(self):
        """Test full capacity check."""
        group = Group.create(subject_id=1, period_id=1, group_number="001", capacity=30)
        group.enrolled_count = 30
        
        assert group.is_full is True
        assert group.can_enroll() is False
    
    def test_add_schedule(self):
        """Test adding schedule to group."""
        group = Group.create(subject_id=1, period_id=1, group_number="001")
        
        group.add_schedule(
            day_of_week=DayOfWeek.MONDAY,
            start_time=time(8, 0),
            end_time=time(10, 0),
            classroom="A101",
        )
        
        assert len(group.schedules) == 1
        assert group.schedules[0].day_of_week == DayOfWeek.MONDAY
    
    def test_schedule_conflict_detection(self):
        """Test schedule conflict detection between groups."""
        schedule1 = Schedule(
            day_of_week=DayOfWeek.MONDAY,
            start_time=time(8, 0),
            end_time=time(10, 0),
        )
        schedule2 = Schedule(
            day_of_week=DayOfWeek.MONDAY,
            start_time=time(9, 0),
            end_time=time(11, 0),
        )
        schedule3 = Schedule(
            day_of_week=DayOfWeek.TUESDAY,
            start_time=time(8, 0),
            end_time=time(10, 0),
        )
        
        # Same day, overlapping times
        assert schedule1.overlaps_with(schedule2) is True
        # Different days
        assert schedule1.overlaps_with(schedule3) is False


class TestEnrollmentEntity:
    """Test suite for Enrollment domain entity."""
    
    def test_create_enrollment(self):
        """Test Enrollment.create() factory method."""
        enrollment = Enrollment.create(
            student_id=1,
            group_id=10,
            subject_code="MAT101",
            subject_name="Math I",
        )
        
        assert enrollment.student_id == 1
        assert enrollment.group_id == 10
        assert enrollment.status == EnrollmentStatus.ENROLLED
        assert enrollment.is_active is True
    
    def test_complete_with_passing_grade(self):
        """Test completing enrollment with passing grade."""
        enrollment = Enrollment.create(student_id=1, group_id=10)
        
        enrollment.complete_with_grade(Decimal("8.5"))
        
        assert enrollment.status == EnrollmentStatus.PASSED
        assert enrollment.was_approved is True
        assert enrollment.grade.letter == "B"
    
    def test_complete_with_failing_grade(self):
        """Test completing enrollment with failing grade."""
        enrollment = Enrollment.create(student_id=1, group_id=10)
        
        enrollment.complete_with_grade(Decimal("5.5"))
        
        assert enrollment.status == EnrollmentStatus.FAILED
        assert enrollment.was_approved is False
        assert enrollment.grade.letter == "F"
    
    def test_drop_enrollment(self):
        """Test dropping an enrollment."""
        enrollment = Enrollment.create(student_id=1, group_id=10)
        
        enrollment.drop()
        
        assert enrollment.status == EnrollmentStatus.DROPPED
        assert enrollment.completed_at is not None
    
    def test_cannot_drop_completed_enrollment(self):
        """Test that completed enrollments cannot be dropped."""
        enrollment = Enrollment.create(student_id=1, group_id=10)
        enrollment.complete_with_grade(Decimal("8.0"))
        
        with pytest.raises(ValueError):
            enrollment.drop()


class TestValueObjects:
    """Test suite for Planning value objects."""
    
    def test_subject_code_validation(self):
        """Test SubjectCode validation."""
        code = SubjectCode("mat101")
        assert str(code) == "MAT101"  # Uppercase
        
        code2 = SubjectCode("CS1234")
        assert code2.department_prefix == "CS"
        assert code2.number == "1234"
    
    def test_credits_validation(self):
        """Test Credits validation."""
        credits = Credits(4)
        assert int(credits) == 4
        
        with pytest.raises(ValueError):
            Credits(0)  # Below minimum
        
        with pytest.raises(ValueError):
            Credits(15)  # Above maximum
    
    def test_grade_conversion(self):
        """Test Grade letter conversion."""
        assert Grade(Decimal("9.5")).letter == "A"
        assert Grade(Decimal("8.0")).letter == "B"
        assert Grade(Decimal("7.0")).letter == "C"
        assert Grade(Decimal("6.0")).letter == "D"
        assert Grade(Decimal("5.0")).letter == "F"
    
    def test_grade_passing_check(self):
        """Test Grade passing check."""
        passing = Grade(Decimal("7.0"))
        failing = Grade(Decimal("5.5"))
        
        assert passing.is_passing is True
        assert failing.is_passing is False
