"""
User and Profile domain entities.
Pure domain objects, no framework dependencies.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from app.domain.value_objects.email import Email


@dataclass
class Profile:
    """User profile entity."""
    first_name: str
    last_name: str
    student_id: Optional[str] = None
    employee_id: Optional[str] = None
    department: Optional[str] = None
    program: Optional[str] = None
    photo_url: Optional[str] = None
    phone: Optional[str] = None
    id: Optional[int] = None
    user_id: Optional[int] = None
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


@dataclass
class User:
    """User domain entity."""
    email: Email
    is_active: bool = True
    is_verified: bool = False
    id: Optional[int] = None
    password_hash: Optional[str] = None
    profile: Optional[Profile] = None
    roles: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def deactivate(self) -> None:
        """Deactivate the user."""
        if not self.is_active:
            raise ValueError("User is already inactive")
        self.is_active = False

    def activate(self) -> None:
        """Activate the user."""
        if self.is_active:
            raise ValueError("User is already active")
        self.is_active = True
    
    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        return role_name in self.roles
    
    def get_role_names(self) -> List[str]:
        """Get list of role names."""
        return self.roles
