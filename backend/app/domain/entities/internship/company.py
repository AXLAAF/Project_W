"""
Company domain entity.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.domain.value_objects.internship import CompanyStatus


@dataclass
class Company:
    """Represents a company partner for internships."""
    name: str
    rfc: str
    contact_email: str
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    is_verified: bool = False
    status: CompanyStatus = CompanyStatus.ACTIVE
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def is_active(self) -> bool:
        """Check if company is active."""
        return self.status == CompanyStatus.ACTIVE and self.is_verified

    def verify(self) -> None:
        """Verify the company."""
        self.is_verified = True
        self.status = CompanyStatus.ACTIVE

    def blacklist(self) -> None:
        """Blacklist the company."""
        self.status = CompanyStatus.BLACKLISTED
