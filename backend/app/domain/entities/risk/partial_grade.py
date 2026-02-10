"""
PartialGrade domain entity.
Pure domain logic for student partial grades/evaluations.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.domain.value_objects.risk import GradeType


@dataclass
class PartialGrade:
    """
    PartialGrade domain entity.
    
    Represents a partial grade/evaluation for a student in a course.
    """
    student_id: int
    group_id: int
    grade_type: GradeType
    name: str  # e.g., "Parcial 1", "Quiz 3"
    grade: Decimal
    graded_at: datetime
    max_grade: Decimal = Decimal("10.0")
    weight: Decimal = Decimal("1.0")  # Percentage weight for final average
    feedback: Optional[str] = None
    recorded_by: Optional[int] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    # Denormalized fields
    student_name: Optional[str] = None
    subject_code: Optional[str] = None
    
    def __post_init__(self):
        if isinstance(self.grade_type, str):
            self.grade_type = GradeType(self.grade_type)
        if isinstance(self.grade, (int, float)):
            self.grade = Decimal(str(self.grade))
        if isinstance(self.max_grade, (int, float)):
            self.max_grade = Decimal(str(self.max_grade))
        if isinstance(self.weight, (int, float)):
            self.weight = Decimal(str(self.weight))
        
        if self.grade < 0:
            raise ValueError("Grade cannot be negative")
        if self.max_grade <= 0:
            raise ValueError("Max grade must be positive")
        if self.grade > self.max_grade:
            raise ValueError(f"Grade {self.grade} cannot exceed max grade {self.max_grade}")
    
    @property
    def normalized_grade(self) -> float:
        """Get grade normalized to 0-10 scale."""
        if self.max_grade == 0:
            return 0.0
        return float(self.grade / self.max_grade * 10)
    
    @property
    def percentage(self) -> float:
        """Get grade as percentage of max."""
        if self.max_grade == 0:
            return 0.0
        return float(self.grade / self.max_grade * 100)
    
    @property
    def is_passing(self) -> bool:
        """Check if grade is passing (>=6 on 10 scale)."""
        return self.normalized_grade >= 6.0
    
    @property
    def letter_grade(self) -> str:
        """Convert to letter grade."""
        normalized = self.normalized_grade
        if normalized >= 9.5:
            return "A+"
        elif normalized >= 9.0:
            return "A"
        elif normalized >= 8.5:
            return "A-"
        elif normalized >= 8.0:
            return "B+"
        elif normalized >= 7.5:
            return "B"
        elif normalized >= 7.0:
            return "B-"
        elif normalized >= 6.5:
            return "C+"
        elif normalized >= 6.0:
            return "C"
        elif normalized >= 5.0:
            return "D"
        else:
            return "F"
    
    def update_grade(
        self,
        new_grade: Decimal,
        recorded_by: int,
        feedback: Optional[str] = None,
    ) -> None:
        """Update the grade value."""
        if new_grade < 0:
            raise ValueError("Grade cannot be negative")
        if new_grade > self.max_grade:
            raise ValueError(f"Grade cannot exceed max grade {self.max_grade}")
        
        self.grade = new_grade
        self.recorded_by = recorded_by
        self.graded_at = datetime.now()
        if feedback:
            self.feedback = feedback
    
    @classmethod
    def record(
        cls,
        student_id: int,
        group_id: int,
        grade_type: GradeType,
        name: str,
        grade: float,
        recorded_by: int,
        max_grade: float = 10.0,
        weight: float = 1.0,
        feedback: Optional[str] = None,
    ) -> "PartialGrade":
        """Factory method to record a grade."""
        return cls(
            student_id=student_id,
            group_id=group_id,
            grade_type=grade_type,
            name=name,
            grade=Decimal(str(grade)),
            max_grade=Decimal(str(max_grade)),
            weight=Decimal(str(weight)),
            feedback=feedback,
            recorded_by=recorded_by,
            graded_at=datetime.now(),
        )
    
    def __repr__(self) -> str:
        return f"PartialGrade(student={self.student_id}, name={self.name}, grade={self.grade}/{self.max_grade})"
