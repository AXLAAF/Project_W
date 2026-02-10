"""
ReservationRule model - Configurable rules for resource reservations.
"""
from datetime import datetime, time
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database import Base

if TYPE_CHECKING:
    from .resource import Resource


class RuleType(str, Enum):
    """Types of reservation rules."""
    HORARIO = "HORARIO"              # Operating hours
    BLOQUEO = "BLOQUEO"              # Blocked time slots
    LIMITE_USUARIO = "LIMITE_USUARIO"  # User reservation limits
    ANTICIPACION = "ANTICIPACION"     # Advance booking requirements


class ReservationRule(Base):
    """
    ReservationRule model for configurable reservation constraints.
    
    Allows administrators to set operating hours, blocked periods,
    and user limits for resources.
    """
    __tablename__ = "reservation_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Resource association (null = applies to all resources)
    resource_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("resources.id"), nullable=True, index=True
    )
    
    # Rule configuration
    rule_type: Mapped[RuleType] = mapped_column(SQLEnum(RuleType), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Time-based rules (for HORARIO and BLOQUEO)
    day_of_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0=Monday, 6=Sunday
    start_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    end_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    
    # Date-based rules (for specific date blocks)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Limit-based rules (for LIMITE_USUARIO)
    max_reservations_per_day: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_reservations_per_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_hours_per_day: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_hours_per_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    resource: Mapped[Optional["Resource"]] = relationship("Resource", back_populates="rules")

    def __repr__(self) -> str:
        return f"<ReservationRule(id={self.id}, type='{self.rule_type}', name='{self.name}')>"
