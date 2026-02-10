"""Enrollment service for business logic."""
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.planning.models.enrollment import Enrollment, EnrollmentStatus
from app.planning.repositories.enrollment_repository import EnrollmentRepository
from app.planning.repositories.group_repository import GroupRepository
from app.planning.schemas.enrollment import AcademicHistoryItem, AcademicHistorySummary


class EnrollmentError(Exception):
    """Base exception for enrollment errors."""
    pass


class GroupFullError(EnrollmentError):
    """Raised when trying to enroll in a full group."""
    pass


class AlreadyEnrolledError(EnrollmentError):
    """Raised when student is already enrolled."""
    pass


class PrerequisiteNotMetError(EnrollmentError):
    """Raised when prerequisites are not met."""

    def __init__(self, message: str, missing: List[str]):
        super().__init__(message)
        self.missing = missing


class EnrollmentService:
    """Service for Enrollment operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.enrollment_repo = EnrollmentRepository(session)
        self.group_repo = GroupRepository(session)

    async def enroll(self, student_id: int, group_id: int) -> Enrollment:
        """Enroll a student in a group."""
        # Check if group exists and has capacity
        group = await self.group_repo.get_by_id(group_id)
        if not group:
            raise EnrollmentError(f"Group with ID {group_id} not found")

        if group.is_full:
            raise GroupFullError(f"Group {group.display_name} is full")

        # Check if already enrolled
        existing = await self.enrollment_repo.get_student_enrollment(student_id, group_id)
        if existing:
            raise AlreadyEnrolledError(
                f"Already enrolled in {group.display_name}"
            )

        # Create enrollment
        enrollment = await self.enrollment_repo.create(student_id, group_id)

        # Increment group count
        await self.group_repo.increment_enrolled(group_id)

        return enrollment

    async def drop(self, student_id: int, enrollment_id: int) -> bool:
        """Drop an enrollment."""
        enrollment = await self.enrollment_repo.get_by_id(enrollment_id)
        if not enrollment:
            raise EnrollmentError(f"Enrollment with ID {enrollment_id} not found")

        if enrollment.student_id != student_id:
            raise EnrollmentError("Cannot drop another student's enrollment")

        if enrollment.status != EnrollmentStatus.ENROLLED.value:
            raise EnrollmentError("Can only drop active enrollments")

        # Update status to dropped
        await self.enrollment_repo.update_status(enrollment_id, EnrollmentStatus.DROPPED)

        # Decrement group count
        await self.group_repo.decrement_enrolled(enrollment.group_id)

        return True

    async def get_current_enrollments(self, student_id: int) -> List[Enrollment]:
        """Get current active enrollments."""
        return await self.enrollment_repo.get_current_enrollments(student_id)

    async def get_history(self, student_id: int) -> AcademicHistorySummary:
        """Get complete academic history with summary."""
        enrollments = await self.enrollment_repo.get_history(student_id)
        credits_summary = await self.enrollment_repo.get_credits_summary(student_id)
        gpa = await self.enrollment_repo.get_gpa(student_id)

        current_items = []
        history_items = []
        passed_count = 0
        failed_count = 0
        in_progress_count = 0

        for enrollment in enrollments:
            item = AcademicHistoryItem(
                enrollment_id=enrollment.id,
                subject={
                    "id": enrollment.group.subject.id,
                    "code": enrollment.group.subject.code,
                    "name": enrollment.group.subject.name,
                    "credits": enrollment.group.subject.credits,
                },
                period={
                    "id": enrollment.group.period.id,
                    "code": enrollment.group.period.code,
                    "name": enrollment.group.period.name,
                },
                group_number=enrollment.group.group_number,
                status=enrollment.status,
                grade=enrollment.grade,
                grade_letter=enrollment.grade_letter,
                attempt_number=enrollment.attempt_number,
                credits_earned=(
                    enrollment.group.subject.credits
                    if enrollment.status == EnrollmentStatus.PASSED.value
                    else 0
                ),
            )

            if enrollment.status == EnrollmentStatus.ENROLLED.value:
                current_items.append(item)
                in_progress_count += 1
            else:
                history_items.append(item)
                if enrollment.status == EnrollmentStatus.PASSED.value:
                    passed_count += 1
                elif enrollment.status == EnrollmentStatus.FAILED.value:
                    failed_count += 1

        return AcademicHistorySummary(
            student_id=student_id,
            total_credits_attempted=credits_summary["total_attempted"],
            total_credits_earned=credits_summary["earned"],
            gpa=round(gpa, 2),
            subjects_passed=passed_count,
            subjects_failed=failed_count,
            subjects_in_progress=in_progress_count,
            current_enrollments=current_items,
            history=history_items,
        )

    async def get_passed_subject_ids(self, student_id: int) -> List[int]:
        """Get IDs of subjects the student has passed."""
        return await self.enrollment_repo.get_passed_subjects(student_id)

    async def record_grade(
        self,
        enrollment_id: int,
        grade: float,
        passed: bool,
    ) -> Enrollment:
        """Record a final grade for an enrollment."""
        status = EnrollmentStatus.PASSED if passed else EnrollmentStatus.FAILED
        enrollment = await self.enrollment_repo.update_status(
            enrollment_id, status, grade
        )
        if not enrollment:
            raise EnrollmentError(f"Enrollment with ID {enrollment_id} not found")
        return enrollment
