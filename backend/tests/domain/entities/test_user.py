"""
Unit tests for User domain entity.
Pure domain tests - no database, no infrastructure.
"""
import pytest
from datetime import datetime

from app.domain.entities.user import User
from app.domain.entities.profile import Profile
from app.domain.entities.role import Role, UserRole
from app.domain.value_objects.email import Email
from app.domain.exceptions import UserAlreadyInactiveError


class TestUserEntity:
    """Test suite for User domain entity."""
    
    def test_create_user_with_valid_email(self):
        """Test creating a user with valid email."""
        user = User(
            email=Email("test@universidad.edu"),
            is_active=True,
            is_verified=False,
        )
        
        assert user.email_str == "test@universidad.edu"
        assert user.is_active is True
        assert user.is_verified is False
    
    def test_create_user_factory_method(self):
        """Test User.create() factory method."""
        profile = Profile(
            first_name="Juan",
            last_name="Pérez",
        )
        
        user = User.create(
            email="juan@universidad.edu",
            password_hash="hashed_password",
            profile=profile,
        )
        
        assert user.email_str == "juan@universidad.edu"
        assert user.password_hash == "hashed_password"
        assert user.profile is not None
        assert user.profile.full_name == "Juan Pérez"
        assert user.is_active is True
        assert user.is_verified is False
    
    def test_deactivate_user(self):
        """Test deactivating a user."""
        user = User(
            id=1,
            email=Email("test@uni.edu"),
            is_active=True,
        )
        
        user.deactivate()
        
        assert user.is_active is False
    
    def test_deactivate_already_inactive_user_raises_error(self):
        """Test that deactivating an already inactive user raises error."""
        user = User(
            id=1,
            email=Email("test@uni.edu"),
            is_active=False,
        )
        
        with pytest.raises(UserAlreadyInactiveError):
            user.deactivate()
    
    def test_activate_user(self):
        """Test activating a user."""
        user = User(
            email=Email("test@uni.edu"),
            is_active=False,
        )
        
        user.activate()
        
        assert user.is_active is True
    
    def test_verify_user(self):
        """Test verifying a user."""
        user = User(
            email=Email("test@uni.edu"),
            is_verified=False,
        )
        
        user.verify()
        
        assert user.is_verified is True
    
    def test_has_role(self):
        """Test checking if user has a role."""
        role = Role(id=1, name="ALUMNO")
        user_role = UserRole(user_id=1, role=role)
        
        user = User(
            id=1,
            email=Email("test@uni.edu"),
            roles=[user_role],
        )
        
        assert user.has_role("ALUMNO") is True
        assert user.has_role("alumno") is True  # Case insensitive
        assert user.has_role("ADMIN_SISTEMA") is False
    
    def test_has_any_role(self):
        """Test checking if user has any of multiple roles."""
        role = Role(id=1, name="PROFESOR")
        user_role = UserRole(user_id=1, role=role)
        
        user = User(
            id=1,
            email=Email("test@uni.edu"),
            roles=[user_role],
        )
        
        assert user.has_any_role(["ALUMNO", "PROFESOR"]) is True
        assert user.has_any_role(["ADMIN_SISTEMA", "COORDINADOR"]) is False
    
    def test_get_role_names(self):
        """Test getting list of role names."""
        roles = [
            UserRole(user_id=1, role=Role(id=1, name="ALUMNO")),
            UserRole(user_id=1, role=Role(id=2, name="PROFESOR")),
        ]
        
        user = User(
            id=1,
            email=Email("test@uni.edu"),
            roles=roles,
        )
        
        role_names = user.get_role_names()
        
        assert "ALUMNO" in role_names
        assert "PROFESOR" in role_names
        assert len(role_names) == 2
    
    def test_add_role(self):
        """Test adding a role to user."""
        user = User(
            id=1,
            email=Email("test@uni.edu"),
            roles=[],
        )
        role = Role(id=1, name="ALUMNO")
        
        user.add_role(role, assigned_by=2)
        
        assert user.has_role("ALUMNO") is True
        assert len(user.roles) == 1
    
    def test_add_role_does_not_duplicate(self):
        """Test that adding same role twice doesn't duplicate."""
        role = Role(id=1, name="ALUMNO")
        user = User(
            id=1,
            email=Email("test@uni.edu"),
            roles=[UserRole(user_id=1, role=role)],
        )
        
        user.add_role(role)
        
        assert len(user.roles) == 1
    
    def test_remove_role(self):
        """Test removing a role from user."""
        role = Role(id=1, name="ALUMNO")
        user = User(
            id=1,
            email=Email("test@uni.edu"),
            roles=[UserRole(user_id=1, role=role)],
        )
        
        result = user.remove_role("ALUMNO")
        
        assert result is True
        assert user.has_role("ALUMNO") is False
        assert len(user.roles) == 0
    
    def test_remove_nonexistent_role(self):
        """Test removing a role user doesn't have."""
        user = User(
            id=1,
            email=Email("test@uni.edu"),
            roles=[],
        )
        
        result = user.remove_role("ADMIN_SISTEMA")
        
        assert result is False
    
    def test_is_admin(self):
        """Test checking if user is admin."""
        admin_role = Role(id=1, name="ADMIN_SISTEMA")
        
        admin = User(
            id=1,
            email=Email("admin@uni.edu"),
            roles=[UserRole(user_id=1, role=admin_role)],
        )
        
        regular = User(
            id=2,
            email=Email("user@uni.edu"),
            roles=[],
        )
        
        assert admin.is_admin() is True
        assert regular.is_admin() is False
    
    def test_is_coordinator_or_above(self):
        """Test checking coordinator level permissions."""
        coord_role = Role(id=1, name="COORDINADOR")
        
        coord = User(
            id=1,
            email=Email("coord@uni.edu"),
            roles=[UserRole(user_id=1, role=coord_role)],
        )
        
        student = User(
            id=2,
            email=Email("student@uni.edu"),
            roles=[UserRole(user_id=2, role=Role(id=2, name="ALUMNO"))],
        )
        
        assert coord.is_coordinator_or_above() is True
        assert student.is_coordinator_or_above() is False
