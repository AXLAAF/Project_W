"""
InternshipPosition model for available internship openings.
"""
import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database import Base

if TYPE_CHECKING:
    from app.internships.models.company import Company
    from app.internships.models.internship_application import InternshipApplication


class PositionModality(str, enum.Enum):
    """Internship modality options."""
    PRESENCIAL = "presencial"
    REMOTO = "remoto"
    HIBRIDO = "hibrido"


class InternshipPosition(Base):
    """Available internship position offered by a company."""

    __tablename__ = "internship_positions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    benefits: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_months: Mapped[int] = mapped_column(Integer, default=6, nullable=False)
    modality: Mapped[PositionModality] = mapped_column(
        Enum(PositionModality), default=PositionModality.PRESENCIAL, nullable=False
    )
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    min_gpa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    min_credits: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    filled_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="positions")
    applications: Mapped[List["InternshipApplication"]] = relationship(
        "InternshipApplication", back_populates="position", cascade="all, delete-orphan"
    )

    @property
    def available_spots(self) -> int:
        """Number of available spots for this position."""
        return self.capacity - self.filled_count

    @property
    def is_available(self) -> bool:
        """Check if position has available spots and is active."""
        return self.is_active and self.available_spots > 0

    def __repr__(self) -> str:
        return f"<InternshipPosition(id={self.id}, title={self.title}, company_id={self.company_id})>"
