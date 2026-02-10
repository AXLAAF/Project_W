"""
ReservationRule domain entity.
"""
from dataclasses import dataclass, field
from datetime import datetime, time, date
from typing import Optional

from app.domain.entities.reservations.resource import Resource
from app.domain.value_objects.reservations import RuleType


@dataclass
class ReservationRule:
    """Represents a rule for resource reservation."""
    rule_type: RuleType
    name: str
    resource_id: Optional[int] = None
    description: Optional[str] = None
    day_of_week: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_reservations_per_day: Optional[int] = None
    max_reservations_per_week: Optional[int] = None
    max_hours_per_day: Optional[int] = None
    max_hours_per_week: Optional[int] = None
    is_active: bool = True
    priority: int = 0
    resource: Optional[Resource] = None
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    def applies_to_resource(self, resource_id: int) -> bool:
        """Check if this rule applies to a specific resource."""
        return self.resource_id is None or self.resource_id == resource_id
