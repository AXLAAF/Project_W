"""
Assignment and AssignmentSubmission domain entities.
Pure domain logic for homework/task tracking.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from app.domain.value_objects.risk import SubmissionStatus


@dataclass
class Assignment:
    """
    Assignment domain entity.
    
    Represents a homework/task definition for a group.
    """
    group_id: int
    title: str
    due_date: datetime
    description: Optional[str] = None
    max_score: float = 100.0
    weight: float = 1.0
    allows_late: bool = True
    late_penalty_percent: float = 10.0  # % penalty per day
    created_by: Optional[int] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    # Denormalized fields
    subject_code: Optional[str] = None
    group_number: Optional[str] = None
    
    submissions: List["AssignmentSubmission"] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.title.strip():
            raise ValueError("Assignment title cannot be empty")
        if self.max_score <= 0:
            raise ValueError("Max score must be positive")
        if self.weight < 0:
            raise ValueError("Weight cannot be negative")
    
    @property
    def is_past_due(self) -> bool:
        """Check if assignment is past due date."""
        now = datetime.now(self.due_date.tzinfo) if self.due_date.tzinfo else datetime.now()
        return now > self.due_date
    
    @property
    def days_until_due(self) -> int:
        """Get days until due date (negative if past due)."""
        now = datetime.now(self.due_date.tzinfo) if self.due_date.tzinfo else datetime.now()
        delta = self.due_date - now
        return delta.days
    
    @property
    def submission_count(self) -> int:
        """Get number of submissions."""
        return len([s for s in self.submissions if s.status.is_submitted])
    
    @property
    def missing_count(self) -> int:
        """Get number of missing submissions."""
        return len([s for s in self.submissions if s.status == SubmissionStatus.MISSING])
    
    def calculate_late_penalty(self, days_late: int) -> float:
        """Calculate penalty for late submission."""
        if not self.allows_late or days_late <= 0:
            return 0.0
        return min(100.0, days_late * self.late_penalty_percent)
    
    def update(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
    ) -> None:
        """Update assignment fields."""
        if title is not None:
            if not title.strip():
                raise ValueError("Title cannot be empty")
            self.title = title.strip()
        if description is not None:
            self.description = description
        if due_date is not None:
            self.due_date = due_date
    
    @classmethod
    def create(
        cls,
        group_id: int,
        title: str,
        due_date: datetime,
        created_by: int,
        description: Optional[str] = None,
        max_score: float = 100.0,
        weight: float = 1.0,
        allows_late: bool = True,
        late_penalty_percent: float = 10.0,
    ) -> "Assignment":
        """Factory method to create an assignment."""
        return cls(
            group_id=group_id,
            title=title.strip(),
            due_date=due_date,
            description=description,
            max_score=max_score,
            weight=weight,
            allows_late=allows_late,
            late_penalty_percent=late_penalty_percent,
            created_by=created_by,
        )
    
    def __repr__(self) -> str:
        return f"Assignment(id={self.id}, title={self.title})"


@dataclass
class AssignmentSubmission:
    """
    AssignmentSubmission domain entity.
    
    Represents a student's submission for an assignment.
    """
    assignment_id: int
    student_id: int
    status: SubmissionStatus = SubmissionStatus.PENDING
    submitted_at: Optional[datetime] = None
    file_url: Optional[str] = None
    comments: Optional[str] = None
    score: Optional[float] = None
    feedback: Optional[str] = None
    graded_at: Optional[datetime] = None
    graded_by: Optional[int] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    # Reference to assignment for late calculations
    assignment: Optional[Assignment] = None
    
    # Denormalized fields
    student_name: Optional[str] = None
    assignment_title: Optional[str] = None
    
    def __post_init__(self):
        if isinstance(self.status, str):
            self.status = SubmissionStatus(self.status)
    
    @property
    def is_late(self) -> bool:
        """Check if submission was late."""
        if self.submitted_at and self.assignment:
            return self.submitted_at > self.assignment.due_date
        return self.status == SubmissionStatus.LATE
    
    @property
    def days_late(self) -> int:
        """Calculate days late."""
        if not self.is_late or not self.submitted_at or not self.assignment:
            return 0
        delta = self.submitted_at - self.assignment.due_date
        return max(0, delta.days)
    
    @property
    def is_submitted(self) -> bool:
        """Check if submission was made."""
        return self.status.is_submitted
    
    @property
    def is_graded(self) -> bool:
        """Check if submission has been graded."""
        return self.status == SubmissionStatus.GRADED
    
    @property
    def adjusted_score(self) -> Optional[float]:
        """Get score adjusted for late penalty."""
        if self.score is None or not self.assignment:
            return self.score
        
        penalty_percent = self.assignment.calculate_late_penalty(self.days_late)
        penalty = self.score * (penalty_percent / 100)
        return max(0, self.score - penalty)
    
    def submit(
        self,
        file_url: Optional[str] = None,
        comments: Optional[str] = None,
    ) -> None:
        """Submit the assignment."""
        if self.status == SubmissionStatus.GRADED:
            raise ValueError("Cannot resubmit a graded assignment")
        
        now = datetime.now()
        self.submitted_at = now
        self.file_url = file_url
        self.comments = comments
        
        if self.assignment and now > self.assignment.due_date:
            self.status = SubmissionStatus.LATE
        else:
            self.status = SubmissionStatus.SUBMITTED
    
    def grade(
        self,
        score: float,
        graded_by: int,
        feedback: Optional[str] = None,
    ) -> None:
        """Grade the submission."""
        if not self.is_submitted:
            raise ValueError("Cannot grade unsubmitted assignment")
        
        if score < 0:
            raise ValueError("Score cannot be negative")
        
        if self.assignment and score > self.assignment.max_score:
            raise ValueError(f"Score cannot exceed max score {self.assignment.max_score}")
        
        self.score = score
        self.graded_by = graded_by
        self.graded_at = datetime.now()
        self.status = SubmissionStatus.GRADED
        if feedback:
            self.feedback = feedback
    
    def mark_missing(self) -> None:
        """Mark submission as missing."""
        if self.status.is_submitted:
            raise ValueError("Cannot mark submitted assignment as missing")
        self.status = SubmissionStatus.MISSING
    
    @classmethod
    def create(
        cls,
        assignment_id: int,
        student_id: int,
        assignment: Optional[Assignment] = None,
    ) -> "AssignmentSubmission":
        """Factory method to create a submission."""
        return cls(
            assignment_id=assignment_id,
            student_id=student_id,
            status=SubmissionStatus.PENDING,
            assignment=assignment,
        )
    
    def __repr__(self) -> str:
        return f"AssignmentSubmission(assignment={self.assignment_id}, student={self.student_id}, status={self.status.value})"


@dataclass
class AssignmentStats:
    """Statistics aggregate for assignment calculations."""
    total_assignments: int = 0
    submitted: int = 0
    late: int = 0
    missing: int = 0
    graded: int = 0
    
    @property
    def on_time_rate(self) -> float:
        """Calculate on-time submission rate as percentage."""
        if self.total_assignments == 0:
            return 100.0
        on_time = self.submitted - self.late
        return (on_time / self.total_assignments) * 100
    
    @property
    def completion_rate(self) -> float:
        """Calculate completion rate as percentage."""
        if self.total_assignments == 0:
            return 100.0
        return (self.submitted / self.total_assignments) * 100
    
    @property
    def missing_rate(self) -> float:
        """Calculate missing rate as percentage."""
        if self.total_assignments == 0:
            return 0.0
        return (self.missing / self.total_assignments) * 100
    
    @classmethod
    def from_submissions(cls, submissions: List[AssignmentSubmission]) -> "AssignmentStats":
        """Create stats from submission records."""
        stats = cls(total_assignments=len(submissions))
        for s in submissions:
            if s.status.is_submitted:
                stats.submitted += 1
            if s.status == SubmissionStatus.LATE:
                stats.late += 1
            if s.status == SubmissionStatus.MISSING:
                stats.missing += 1
            if s.status == SubmissionStatus.GRADED:
                stats.graded += 1
        return stats
