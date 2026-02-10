"""
UserSanction model - Tracks user sanctions for reservation violations.
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database import Base


class SanctionType(str, Enum):
    """Types of sanctions."""
    ADVERTENCIA = "ADVERTENCIA"
    SUSPENSION_TEMPORAL = "SUSPENSION_TEMPORAL"
    SUSPENSION_PERMANENTE = "SUSPENSION_PERMANENTE"


class SanctionReason(str, Enum):
    """Reasons for sanctions."""
    NO_SHOW = "NO_SHOW"
    CANCELACION_TARDIA = "CANCELACION_TARDIA"
    MAL_USO = "MAL_USO"
    DANO_EQUIPO = "DANO_EQUIPO"
    COMPORTAMIENTO = "COMPORTAMIENTO"
    OTRO = "OTRO"


class UserSanction(Base):
    """
    UserSanction model for tracking reservation violations.
    
    Records sanctions applied to users for no-shows, late cancellations,
    or other violations of reservation policies.
    """
    __tablename__ = "user_sanctions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # User being sanctioned
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    
    # Related reservation (if applicable)
    reservation_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("reservations.id"), nullable=True
    )
    
    # Sanction details
    sanction_type: Mapped[SanctionType] = mapped_column(
        SQLEnum(SanctionType), nullable=False
    )
    reason: Mapped[SanctionReason] = mapped_column(
        SQLEnum(SanctionReason), nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Duration (for temporary suspensions)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Applied by
    applied_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    
    # Resolution
    is_resolved: Mapped[bool] = mapped_column(default=False, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<UserSanction(id={self.id}, user_id={self.user_id}, type='{self.sanction_type}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if the sanction is currently active."""
        if self.is_resolved:
            return False
        if self.end_date and datetime.now(self.end_date.tzinfo) > self.end_date:
            return False
        return True
