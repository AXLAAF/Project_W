"""
InternshipApplication model for student applications to internship positions.
"""
import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database import Base

if TYPE_CHECKING:
    from app.core.models.user import User
    from app.internships.models.internship_position import InternshipPosition
    from app.internships.models.internship import Internship


class ApplicationStatus(str, enum.Enum):
    """Application status options."""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class InternshipApplication(Base):
    """Student application to an internship position."""

    __tablename__ = "internship_applications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position_id: Mapped[int] = mapped_column(
        ForeignKey("internship_positions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False
    )
    cv_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cover_letter: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    additional_documents: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewer_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reviewer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    reviewer: Mapped[Optional["User"]] = relationship("User", foreign_keys=[reviewer_id])
    position: Mapped["InternshipPosition"] = relationship(
        "InternshipPosition", back_populates="applications"
    )
    internship: Mapped[Optional["Internship"]] = relationship(
        "Internship", back_populates="application", uselist=False
    )

    def __repr__(self) -> str:
        return f"<InternshipApplication(id={self.id}, user_id={self.user_id}, position_id={self.position_id}, status={self.status})>"
