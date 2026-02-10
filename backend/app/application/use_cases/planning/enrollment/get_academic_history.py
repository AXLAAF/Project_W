"""
Get academic history use case.
Application layer for retrieving student's academic history.
"""
from dataclasses import dataclass
from typing import List, Optional
from decimal import Decimal

from app.domain.repositories.enrollment_repository import IEnrollmentRepository
from app.domain.entities.planning.enrollment import EnrollmentStatus


@dataclass
class EnrollmentHistoryDTO:
    """Single enrollment in history."""
    id: int
    subject_code: str
    subject_name: str
    status: str
    grade: Optional[float]
    grade_letter: Optional[str]
    attempt_number: int
    period_name: Optional[str]
    enrolled_at: str
    completed_at: Optional[str]


@dataclass
class AcademicSummaryDTO:
    """Summary statistics of academic history."""
    total_subjects_passed: int
    total_subjects_failed: int
    total_credits_earned: int
    total_credits_attempted: int
    overall_gpa: float
    current_enrollments: int


@dataclass
class AcademicHistoryDTO:
    """Complete academic history response."""
    student_id: int
    enrollments: List[EnrollmentHistoryDTO]
    summary: AcademicSummaryDTO


class GetAcademicHistoryUseCase:
    """
    Use case for retrieving a student's academic history.
    
    Provides:
    - Complete enrollment history
    - Statistics (GPA, credits, pass/fail counts)
    - Current enrollments
    """
    
    def __init__(self, enrollment_repo: IEnrollmentRepository):
        self._enrollment_repo = enrollment_repo
    
    async def execute(self, student_id: int) -> AcademicHistoryDTO:
        """
        Get complete academic history for a student.
        
        Args:
            student_id: ID of the student
        
        Returns:
            AcademicHistoryDTO with enrollments and summary
        """
        # Get all enrollments
        enrollments = await self._enrollment_repo.get_academic_history(student_id)
        
        # Convert to DTOs and calculate statistics
        enrollment_dtos = []
        total_passed = 0
        total_failed = 0
        total_credits_earned = 0
        total_credits_attempted = 0
        grade_sum = Decimal("0")
        grade_count = 0
        current_count = 0
        
        for enrollment in enrollments:
            # Create DTO
            dto = EnrollmentHistoryDTO(
                id=enrollment.id,
                subject_code=enrollment.subject_code or "",
                subject_name=enrollment.subject_name or "",
                status=enrollment.status.value if isinstance(enrollment.status, EnrollmentStatus) else enrollment.status,
                grade=float(enrollment.grade_value) if enrollment.grade_value else None,
                grade_letter=enrollment.grade_letter,
                attempt_number=enrollment.attempt_number,
                period_name=None,  # Would need to join with period
                enrolled_at=enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else "",
                completed_at=enrollment.completed_at.isoformat() if enrollment.completed_at else None,
            )
            enrollment_dtos.append(dto)
            
            # Calculate statistics
            status = enrollment.status
            if isinstance(status, str):
                status = EnrollmentStatus(status)
            
            if status == EnrollmentStatus.PASSED:
                total_passed += 1
                # Assume 4 credits per subject (would need subject info)
                total_credits_earned += 4
                total_credits_attempted += 4
                if enrollment.grade_value:
                    grade_sum += enrollment.grade_value
                    grade_count += 1
            elif status == EnrollmentStatus.FAILED:
                total_failed += 1
                total_credits_attempted += 4
                if enrollment.grade_value:
                    grade_sum += enrollment.grade_value
                    grade_count += 1
            elif status == EnrollmentStatus.ENROLLED:
                current_count += 1
        
        # Calculate GPA (0-10 scale to 0-4 scale)
        gpa = 0.0
        if grade_count > 0:
            avg_grade = float(grade_sum / grade_count)
            gpa = (avg_grade / 10) * 4  # Convert 0-10 to 0-4
        
        summary = AcademicSummaryDTO(
            total_subjects_passed=total_passed,
            total_subjects_failed=total_failed,
            total_credits_earned=total_credits_earned,
            total_credits_attempted=total_credits_attempted,
            overall_gpa=round(gpa, 2),
            current_enrollments=current_count,
        )
        
        return AcademicHistoryDTO(
            student_id=student_id,
            enrollments=enrollment_dtos,
            summary=summary,
        )
