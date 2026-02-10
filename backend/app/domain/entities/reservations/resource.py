"""
Resource domain entity.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from app.domain.value_objects.reservations import ResourceType, ResourceStatus


@dataclass
class Resource:
    """Represents a reservable resource."""
    name: str
    code: str
    resource_type: ResourceType
    description: Optional[str] = None
    location: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[str] = None
    capacity: Optional[int] = None
    features: Optional[str] = None
    status: ResourceStatus = ResourceStatus.DISPONIBLE
    is_active: bool = True
    image_url: Optional[str] = None
    min_reservation_minutes: int = 30
    max_reservation_minutes: int = 240
    advance_booking_days: int = 14
    requires_approval: bool = False
    responsible_user_id: Optional[int] = None
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    def is_available(self) -> bool:
        """Check if resource is potentially available (active and not strictly unavailable)."""
        return self.is_active and self.status == ResourceStatus.DISPONIBLE

    def set_maintenance(self) -> None:
        """Set resource to maintenance mode."""
        self.status = ResourceStatus.MANTENIMIENTO

    def set_available(self) -> None:
        """Set resource to available mode."""
        self.status = ResourceStatus.DISPONIBLE
