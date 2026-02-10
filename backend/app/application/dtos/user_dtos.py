"""
Data Transfer Objects (DTOs) for user-related use cases.
These are simple data containers for transferring data between layers.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class ProfileDTO:
    """DTO for profile data."""
    id: int
    user_id: int
    first_name: str
    last_name: str
    full_name: str
    student_id: Optional[str] = None
    employee_id: Optional[str] = None
    department: Optional[str] = None
    program: Optional[str] = None
    photo_url: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class UserProfileDTO:
    """DTO for user profile response."""
    id: int
    email: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    profile: Optional[ProfileDTO] = None
    roles: List[str] = None
    
    def __post_init__(self):
        if self.roles is None:
            self.roles = []


@dataclass
class ProfileUpdateDTO:
    """DTO for profile update request."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    program: Optional[str] = None
    phone: Optional[str] = None
    photo_url: Optional[str] = None


@dataclass
class UserUpdateDTO:
    """DTO for user update request (admin)."""
    email: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


@dataclass
class UserListDTO:
    """DTO for paginated user list response."""
    items: List[UserProfileDTO]
    total: int
    page: int
    page_size: int
    total_pages: int


@dataclass
class ProfileCreateDTO:
    """DTO for profile creation."""
    first_name: str
    last_name: str
    student_id: Optional[str] = None
    employee_id: Optional[str] = None
    department: Optional[str] = None
    program: Optional[str] = None
    phone: Optional[str] = None


@dataclass
class RegisterUserDTO:
    """DTO for user registration request."""
    email: str
    password: str
    profile: ProfileCreateDTO


@dataclass
class LoginDTO:
    """DTO for login request."""
    email: str
    password: str


@dataclass
class TokenResponseDTO:
    """DTO for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 0
