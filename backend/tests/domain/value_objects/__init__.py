"""
Unit tests for Email value object.
"""
import pytest

from app.domain.value_objects.email import Email


class TestEmailValueObject:
    """Test suite for Email value object."""
    
    def test_create_valid_email(self):
        """Test creating email with valid format."""
        email = Email("test@universidad.edu")
        
        assert str(email) == "test@universidad.edu"
        assert email.value == "test@universidad.edu"
    
    def test_email_with_subdomain(self):
        """Test email with subdomain."""
        email = Email("user@mail.university.edu")
        
        assert email.domain == "mail.university.edu"
    
    def test_invalid_email_without_at_symbol(self):
        """Test that email without @ raises error."""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("invalidemail.com")
    
    def test_invalid_email_empty(self):
        """Test that empty email raises error."""
        with pytest.raises(ValueError, match="Email cannot be empty"):
            Email("")
    
    def test_invalid_email_no_domain(self):
        """Test that email without domain raises error."""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("user@")
    
    def test_invalid_email_no_local_part(self):
        """Test that email without local part raises error."""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("@domain.com")
    
    def test_email_domain_property(self):
        """Test extracting domain from email."""
        email = Email("juan.perez@universidad.edu")
        
        assert email.domain == "universidad.edu"
    
    def test_email_local_part_property(self):
        """Test extracting local part from email."""
        email = Email("juan.perez@universidad.edu")
        
        assert email.local_part == "juan.perez"
    
    def test_is_institutional_matching_domain(self):
        """Test checking if email is from institutional domain."""
        email = Email("student@universidad.edu")
        
        assert email.is_institutional("universidad.edu") is True
    
    def test_is_institutional_non_matching_domain(self):
        """Test checking if email is not from institutional domain."""
        email = Email("personal@gmail.com")
        
        assert email.is_institutional("universidad.edu") is False
    
    def test_email_equality(self):
        """Test that two emails with same value are equal."""
        email1 = Email("test@uni.edu")
        email2 = Email("test@uni.edu")
        
        assert email1 == email2
    
    def test_email_immutability(self):
        """Test that email value cannot be changed."""
        email = Email("test@uni.edu")
        
        with pytest.raises(AttributeError):
            email.value = "other@uni.edu"
    
    def test_email_hashable(self):
        """Test that email can be used in sets/dicts."""
        email1 = Email("test@uni.edu")
        email2 = Email("test@uni.edu")
        email3 = Email("other@uni.edu")
        
        email_set = {email1, email2, email3}
        
        assert len(email_set) == 2
