"""
Subject and Prerequisites models.
"""
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database import Base

if TYPE_CHECKING:
    from app.planning.models.group import Group


class Subject(Base):
    """Academic subject/course definition."""

    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    credits: Mapped[int] = mapped_column(Integer, nullable=False)
    hours_theory: Mapped[int] = mapped_column(Integer, default=0)
    hours_practice: Mapped[int] = mapped_column(Integer, default=0)
    hours_lab: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    semester_suggested: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    prerequisites: Mapped[List["SubjectPrerequisite"]] = relationship(
        "SubjectPrerequisite",
        foreign_keys="SubjectPrerequisite.subject_id",
        back_populates="subject",
        cascade="all, delete-orphan",
    )
    required_by: Mapped[List["SubjectPrerequisite"]] = relationship(
        "SubjectPrerequisite",
        foreign_keys="SubjectPrerequisite.prerequisite_id",
        back_populates="prerequisite",
    )
    groups: Mapped[List["Group"]] = relationship(
        "Group", back_populates="subject", cascade="all, delete-orphan"
    )

    @property
    def total_hours(self) -> int:
        return self.hours_theory + self.hours_practice + self.hours_lab

    def __repr__(self) -> str:
        return f"<Subject(code={self.code}, name={self.name})>"


class SubjectPrerequisite(Base):
    """Prerequisite relationship between subjects."""

    __tablename__ = "subject_prerequisites"
    __table_args__ = (
        UniqueConstraint("subject_id", "prerequisite_id", name="uq_subject_prerequisite"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )
    prerequisite_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )
    is_mandatory: Mapped[bool] = mapped_column(default=True)  # vs recommended

    # Relationships
    subject: Mapped["Subject"] = relationship(
        "Subject", foreign_keys=[subject_id], back_populates="prerequisites"
    )
    prerequisite: Mapped["Subject"] = relationship(
        "Subject", foreign_keys=[prerequisite_id], back_populates="required_by"
    )

    def __repr__(self) -> str:
        return f"<SubjectPrerequisite(subject={self.subject_id}, prereq={self.prerequisite_id})>"
