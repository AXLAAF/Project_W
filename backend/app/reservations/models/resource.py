"""
Resource model - Represents reservable resources like rooms, labs, equipment.
"""
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database import Base

if TYPE_CHECKING:
    from .reservation import Reservation
    from .reservation_rule import ReservationRule


class ResourceType(str, Enum):
    """Types of reservable resources."""
    SALA_CONFERENCIAS = "SALA_CONFERENCIAS"
    LABORATORIO = "LABORATORIO"
    AUDITORIO = "AUDITORIO"
    SALA_ESTUDIO = "SALA_ESTUDIO"
    EQUIPO = "EQUIPO"
    VEHICULO = "VEHICULO"
    OTRO = "OTRO"


class ResourceStatus(str, Enum):
    """Resource availability status."""
    DISPONIBLE = "DISPONIBLE"
    MANTENIMIENTO = "MANTENIMIENTO"
    FUERA_SERVICIO = "FUERA_SERVICIO"


class Resource(Base):
    """
    Resource model for reservable items.
    
    Represents physical spaces or equipment that can be reserved
    by users for specific time slots.
    """
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Basic information
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resource_type: Mapped[ResourceType] = mapped_column(
        SQLEnum(ResourceType), nullable=False, index=True
    )
    
    # Location and capacity
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    building: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    floor: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Features and equipment (JSON-like string for simplicity)
    features: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status and availability
    status: Mapped[ResourceStatus] = mapped_column(
        SQLEnum(ResourceStatus), default=ResourceStatus.DISPONIBLE, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Images
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Reservation settings
    min_reservation_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    max_reservation_minutes: Mapped[int] = mapped_column(Integer, default=240, nullable=False)
    advance_booking_days: Mapped[int] = mapped_column(Integer, default=14, nullable=False)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Responsible person
    responsible_user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    reservations: Mapped[List["Reservation"]] = relationship(
        "Reservation", back_populates="resource", cascade="all, delete-orphan"
    )
    rules: Mapped[List["ReservationRule"]] = relationship(
        "ReservationRule", back_populates="resource", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Resource(id={self.id}, code='{self.code}', name='{self.name}')>"
