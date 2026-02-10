"""
Reservation domain entity.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.domain.entities.reservations.resource import Resource
from app.domain.value_objects.reservations import ReservationStatus, TimeSlot


@dataclass
class Reservation:
    """Represents a booking of a resource."""
    resource_id: int
    user_id: int
    start_time: datetime
    end_time: datetime
    title: str
    description: Optional[str] = None
    attendees_count: Optional[int] = None
    status: ReservationStatus = ReservationStatus.PENDING
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    checked_in_at: Optional[datetime] = None
    checked_out_at: Optional[datetime] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    parent_reservation_id: Optional[int] = None
    resource: Optional[Resource] = None
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def time_slot(self) -> TimeSlot:
        """Get the time slot for this reservation."""
        return TimeSlot(self.start_time, self.end_time)

    def approve(self, approver_id: int) -> None:
        """Approve the reservation."""
        self.status = ReservationStatus.APPROVED
        self.approved_by_id = approver_id
        self.approved_at = datetime.now()

    def reject(self, reason: str) -> None:
        """Reject the reservation."""
        self.status = ReservationStatus.REJECTED
        self.rejection_reason = reason

    def cancel(self) -> None:
        """Cancel the reservation."""
        self.status = ReservationStatus.CANCELLED

    def check_in(self) -> None:
        """Mark reservation as checked in."""
        self.checked_in_at = datetime.now()

    def check_out(self) -> None:
        """Mark reservation as checked out."""
        self.checked_out_at = datetime.now()
        self.status = ReservationStatus.COMPLETED

    def complete(self) -> None:
        """Mark reservation as completed."""
        self.status = ReservationStatus.COMPLETED
