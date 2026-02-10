"""
Unit tests for Profile domain entity.
"""
import pytest

from app.domain.entities.profile import Profile


class TestProfileEntity:
    """Test suite for Profile domain entity."""
    
    def test_create_profile_with_required_fields(self):
        """Test creating profile with only required fields."""
        profile = Profile(first_name="Juan", last_name="Pérez")
        
        assert profile.first_name == "Juan"
        assert profile.last_name == "Pérez"
        assert profile.full_name == "Juan Pérez"
    
    def test_create_profile_with_all_fields(self):
        """Test creating profile with all fields."""
        profile = Profile(
            id=1,
            user_id=1,
            first_name="María",
            last_name="García",
            student_id="A01234567",
            department="Ingeniería",
            program="Sistemas Computacionales",
            phone="+52 555 123 4567",
        )
        
        assert profile.student_id == "A01234567"
        assert profile.is_student() is True
    
    def test_empty_first_name_raises_error(self):
        """Test that empty first name raises error."""
        with pytest.raises(ValueError, match="First name cannot be empty"):
            Profile(first_name="", last_name="Pérez")
    
    def test_empty_last_name_raises_error(self):
        """Test that empty last name raises error."""
        with pytest.raises(ValueError, match="Last name cannot be empty"):
            Profile(first_name="Juan", last_name="")
    
    def test_whitespace_only_first_name_raises_error(self):
        """Test that whitespace-only first name raises error."""
        with pytest.raises(ValueError, match="First name cannot be empty"):
            Profile(first_name="   ", last_name="Pérez")
    
    def test_full_name_property(self):
        """Test full_name property."""
        profile = Profile(first_name="Ana", last_name="López")
        
        assert profile.full_name == "Ana López"
    
    def test_update_profile_fields(self):
        """Test updating profile fields."""
        profile = Profile(first_name="Juan", last_name="Pérez")
        
        profile.update(
            first_name="Carlos",
            department="Ciencias",
            phone="+52 555 987 6543",
        )
        
        assert profile.first_name == "Carlos"
        assert profile.last_name == "Pérez"  # Unchanged
        assert profile.department == "Ciencias"
        assert profile.phone == "+52 555 987 6543"
    
    def test_update_with_none_does_not_change_field(self):
        """Test that updating with None doesn't change field."""
        profile = Profile(
            first_name="Juan",
            last_name="Pérez",
            department="Ingeniería",
        )
        
        profile.update(first_name=None, department="Ciencias")
        
        assert profile.first_name == "Juan"
        assert profile.department == "Ciencias"
    
    def test_update_with_empty_name_raises_error(self):
        """Test that updating with empty name raises error."""
        profile = Profile(first_name="Juan", last_name="Pérez")
        
        with pytest.raises(ValueError, match="First name cannot be empty"):
            profile.update(first_name="")
    
    def test_is_student(self):
        """Test is_student check."""
        student = Profile(
            first_name="Juan",
            last_name="Pérez",
            student_id="A01234567",
        )
        
        employee = Profile(
            first_name="María",
            last_name="García",
            employee_id="E001",
        )
        
        assert student.is_student() is True
        assert employee.is_student() is False
    
    def test_is_employee(self):
        """Test is_employee check."""
        student = Profile(
            first_name="Juan",
            last_name="Pérez",
            student_id="A01234567",
        )
        
        employee = Profile(
            first_name="María",
            last_name="García",
            employee_id="E001",
        )
        
        assert student.is_employee() is False
        assert employee.is_employee() is True
