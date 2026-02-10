"""
Profile domain entity.
Pure domain model without any infrastructure dependencies.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Profile:
    """
    User profile domain entity.
    
    Contains additional user information beyond authentication.
    This is a pure domain object with no infrastructure dependencies.
    """
    first_name: str
    last_name: str
    user_id: Optional[int] = None
    id: Optional[int] = None
    student_id: Optional[str] = None
    employee_id: Optional[str] = None
    department: Optional[str] = None
    program: Optional[str] = None
    photo_url: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self) -> None:
        """Validate profile data after initialization."""
        if not self.first_name or not self.first_name.strip():
            raise ValueError("First name cannot be empty")
        if not self.last_name or not self.last_name.strip():
            raise ValueError("Last name cannot be empty")
    
    @property
    def full_name(self) -> str:
        """Get the full name of the user."""
        return f"{self.first_name} {self.last_name}"
    
    def update(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        department: Optional[str] = None,
        program: Optional[str] = None,
        phone: Optional[str] = None,
        photo_url: Optional[str] = None,
    ) -> None:
        """
        Update profile fields.
        
        Only updates fields that are explicitly provided (not None).
        """
        if first_name is not None:
            if not first_name.strip():
                raise ValueError("First name cannot be empty")
            self.first_name = first_name
        
        if last_name is not None:
            if not last_name.strip():
                raise ValueError("Last name cannot be empty")
            self.last_name = last_name
        
        if department is not None:
            self.department = department
        
        if program is not None:
            self.program = program
        
        if phone is not None:
            self.phone = phone
        
        if photo_url is not None:
            self.photo_url = photo_url
    
    def is_student(self) -> bool:
        """Check if this profile belongs to a student."""
        return self.student_id is not None
    
    def is_employee(self) -> bool:
        """Check if this profile belongs to an employee."""
        return self.employee_id is not None
