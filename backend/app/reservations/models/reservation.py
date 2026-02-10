"""
Reservation model - Represents a booking of a resource.
"""
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database import Base

if TYPE_CHECKING:
    from .resource import Resource


class ReservationStatus(str, Enum):
    """Status of a reservation."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"


class Reservation(Base):
    """
    Reservation model for resource bookings.
    
    Represents a time slot reservation for a specific resource by a user.
    """
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Resource and user
    resource_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("resources.id"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    
    # Time slot
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Reservation details
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    attendees_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Status
    status: Mapped[ReservationStatus] = mapped_column(
        SQLEnum(ReservationStatus), default=ReservationStatus.PENDING, nullable=False, index=True
    )
    
    # Approval
    approved_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Check-in/out
    checked_in_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    checked_out_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Recurrence (for recurring reservations)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recurrence_pattern: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    parent_reservation_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("reservations.id"), nullable=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    resource: Mapped["Resource"] = relationship("Resource", back_populates="reservations")

    def __repr__(self) -> str:
        return f"<Reservation(id={self.id}, resource_id={self.resource_id}, status='{self.status}')>"
    
    @property
    def duration_minutes(self) -> int:
        """Calculate the duration of the reservation in minutes."""
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)
