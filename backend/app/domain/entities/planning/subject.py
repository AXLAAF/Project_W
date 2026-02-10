"""
Subject domain entity.
Pure domain logic for academic subjects/courses.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from app.domain.value_objects.planning import SubjectCode, Credits


@dataclass
class Prerequisite:
    """
    Prerequisite relationship value object.
    Represents a prerequisite requirement for a subject.
    """
    prerequisite_subject_id: int
    prerequisite_code: str
    prerequisite_name: str
    is_mandatory: bool = True
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Prerequisite):
            return False
        return self.prerequisite_subject_id == other.prerequisite_subject_id


@dataclass
class Subject:
    """
    Subject domain entity (aggregate root).
    
    Represents an academic subject/course with its attributes
    and business logic.
    """
    code: SubjectCode
    name: str
    credits: Credits
    hours_theory: int = 0
    hours_practice: int = 0
    hours_lab: int = 0
    description: Optional[str] = None
    department: Optional[str] = None
    semester_suggested: Optional[int] = None
    is_active: bool = True
    id: Optional[int] = None
    prerequisites: List[Prerequisite] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if isinstance(self.code, str):
            self.code = SubjectCode(self.code)
        if isinstance(self.credits, int):
            self.credits = Credits(self.credits)
    
    @property
    def code_str(self) -> str:
        """Get code as string."""
        return str(self.code)
    
    @property
    def credits_value(self) -> int:
        """Get credits as integer."""
        return self.credits.value
    
    @property
    def total_hours(self) -> int:
        """Calculate total hours (theory + practice + lab)."""
        return self.hours_theory + self.hours_practice + self.hours_lab
    
    def has_prerequisite(self, subject_id: int) -> bool:
        """Check if this subject has a specific prerequisite."""
        return any(p.prerequisite_subject_id == subject_id for p in self.prerequisites)
    
    def get_mandatory_prerequisites(self) -> List[Prerequisite]:
        """Get only mandatory prerequisites."""
        return [p for p in self.prerequisites if p.is_mandatory]
    
    def add_prerequisite(
        self,
        prerequisite_subject_id: int,
        prerequisite_code: str,
        prerequisite_name: str,
        is_mandatory: bool = True,
    ) -> None:
        """Add a prerequisite to this subject."""
        if self.has_prerequisite(prerequisite_subject_id):
            return  # Already exists
        
        if prerequisite_subject_id == self.id:
            raise ValueError("A subject cannot be its own prerequisite")
        
        self.prerequisites.append(Prerequisite(
            prerequisite_subject_id=prerequisite_subject_id,
            prerequisite_code=prerequisite_code,
            prerequisite_name=prerequisite_name,
            is_mandatory=is_mandatory,
        ))
    
    def remove_prerequisite(self, prerequisite_subject_id: int) -> bool:
        """Remove a prerequisite. Returns True if removed."""
        for i, prereq in enumerate(self.prerequisites):
            if prereq.prerequisite_subject_id == prerequisite_subject_id:
                self.prerequisites.pop(i)
                return True
        return False
    
    def deactivate(self) -> None:
        """Deactivate this subject."""
        if not self.is_active:
            raise ValueError("Subject is already inactive")
        self.is_active = False
    
    def activate(self) -> None:
        """Activate this subject."""
        self.is_active = True
    
    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        department: Optional[str] = None,
        semester_suggested: Optional[int] = None,
        hours_theory: Optional[int] = None,
        hours_practice: Optional[int] = None,
        hours_lab: Optional[int] = None,
    ) -> None:
        """Update subject fields."""
        if name is not None:
            if not name.strip():
                raise ValueError("Subject name cannot be empty")
            self.name = name.strip()
        if description is not None:
            self.description = description
        if department is not None:
            self.department = department
        if semester_suggested is not None:
            if semester_suggested < 1 or semester_suggested > 12:
                raise ValueError("Semester must be between 1 and 12")
            self.semester_suggested = semester_suggested
        if hours_theory is not None:
            if hours_theory < 0:
                raise ValueError("Hours cannot be negative")
            self.hours_theory = hours_theory
        if hours_practice is not None:
            if hours_practice < 0:
                raise ValueError("Hours cannot be negative")
            self.hours_practice = hours_practice
        if hours_lab is not None:
            if hours_lab < 0:
                raise ValueError("Hours cannot be negative")
            self.hours_lab = hours_lab
    
    @classmethod
    def create(
        cls,
        code: str,
        name: str,
        credits: int,
        hours_theory: int = 0,
        hours_practice: int = 0,
        hours_lab: int = 0,
        description: Optional[str] = None,
        department: Optional[str] = None,
        semester_suggested: Optional[int] = None,
    ) -> "Subject":
        """Factory method to create a new subject."""
        if not name.strip():
            raise ValueError("Subject name cannot be empty")
        
        return cls(
            code=SubjectCode(code),
            name=name.strip(),
            credits=Credits(credits),
            hours_theory=hours_theory,
            hours_practice=hours_practice,
            hours_lab=hours_lab,
            description=description,
            department=department,
            semester_suggested=semester_suggested,
            is_active=True,
        )
    
    def __repr__(self) -> str:
        return f"Subject(code={self.code}, name={self.name})"
