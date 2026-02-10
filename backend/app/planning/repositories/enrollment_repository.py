"""Enrollment repository for database operations."""
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.planning.models.enrollment import Enrollment, EnrollmentStatus
from app.planning.models.group import Group
from app.planning.models.subject import Subject


class EnrollmentRepository:
    """Repository for Enrollment operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, student_id: int, group_id: int) -> Enrollment:
        """Create a new enrollment."""
        # Count previous attempts for this subject
        attempt = await self._count_attempts(student_id, group_id)

        enrollment = Enrollment(
            student_id=student_id,
            group_id=group_id,
            attempt_number=attempt + 1,
        )
        self.session.add(enrollment)
        return enrollment

    async def _count_attempts(self, student_id: int, group_id: int) -> int:
        """Count previous enrollment attempts for the same subject."""
        # Get the subject_id for this group
        group_result = await self.session.execute(
            select(Group.subject_id).where(Group.id == group_id)
        )
        subject_id = group_result.scalar_one_or_none()
        if not subject_id:
            return 0

        # Count previous enrollments in any group of this subject
        result = await self.session.execute(
            select(func.count(Enrollment.id))
            .join(Group, Enrollment.group_id == Group.id)
            .where(
                Enrollment.student_id == student_id,
                Group.subject_id == subject_id,
            )
        )
        return result.scalar_one() or 0

    async def get_by_id(self, enrollment_id: int) -> Optional[Enrollment]:
        """Get enrollment by ID."""
        result = await self.session.execute(
            select(Enrollment)
            .options(
                selectinload(Enrollment.group).selectinload(Group.subject),
                selectinload(Enrollment.group).selectinload(Group.schedules),
            )
            .where(Enrollment.id == enrollment_id)
        )
        return result.scalar_one_or_none()

    async def get_student_enrollment(
        self, student_id: int, group_id: int
    ) -> Optional[Enrollment]:
        """Get a specific student enrollment."""
        result = await self.session.execute(
            select(Enrollment).where(
                Enrollment.student_id == student_id,
                Enrollment.group_id == group_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_current_enrollments(self, student_id: int) -> List[Enrollment]:
        """Get current active enrollments for a student."""
        result = await self.session.execute(
            select(Enrollment)
            .options(
                selectinload(Enrollment.group).selectinload(Group.subject),
                selectinload(Enrollment.group).selectinload(Group.schedules),
                selectinload(Enrollment.group).selectinload(Group.period),
            )
            .where(
                Enrollment.student_id == student_id,
                Enrollment.status == EnrollmentStatus.ENROLLED.value,
            )
        )
        return list(result.scalars().all())

    async def get_history(self, student_id: int) -> List[Enrollment]:
        """Get complete enrollment history for a student."""
        result = await self.session.execute(
            select(Enrollment)
            .options(
                selectinload(Enrollment.group).selectinload(Group.subject),
                selectinload(Enrollment.group).selectinload(Group.period),
            )
            .where(Enrollment.student_id == student_id)
            .order_by(Enrollment.enrolled_at.desc())
        )
        return list(result.scalars().all())

    async def get_passed_subjects(self, student_id: int) -> List[int]:
        """Get IDs of subjects the student has passed."""
        result = await self.session.execute(
            select(Group.subject_id)
            .join(Enrollment, Enrollment.group_id == Group.id)
            .where(
                Enrollment.student_id == student_id,
                Enrollment.status == EnrollmentStatus.PASSED.value,
            )
            .distinct()
        )
        return [row[0] for row in result.all()]

    async def update_status(
        self, enrollment_id: int, status: EnrollmentStatus, grade: Optional[float] = None
    ) -> Optional[Enrollment]:
        """Update enrollment status and grade."""
        enrollment = await self.get_by_id(enrollment_id)
        if not enrollment:
            return None

        enrollment.status = status.value
        if grade is not None:
            enrollment.grade = grade
            enrollment.grade_letter = enrollment.calculate_grade_letter()

        if status in (EnrollmentStatus.PASSED, EnrollmentStatus.FAILED):
            from datetime import datetime, timezone
            enrollment.completed_at = datetime.now(timezone.utc)

        return enrollment

    async def delete(self, enrollment_id: int) -> bool:
        """Delete an enrollment (drop course)."""
        enrollment = await self.get_by_id(enrollment_id)
        if enrollment:
            await self.session.delete(enrollment)
            return True
        return False

    async def get_gpa(self, student_id: int) -> float:
        """Calculate GPA for a student."""
        result = await self.session.execute(
            select(
                func.sum(Enrollment.grade * Group.subject.credits),
                func.sum(Group.subject.credits),
            )
            .select_from(Enrollment)
            .join(Group, Enrollment.group_id == Group.id)
            .join(Subject, Group.subject_id == Subject.id)
            .where(
                Enrollment.student_id == student_id,
                Enrollment.status == EnrollmentStatus.PASSED.value,
                Enrollment.grade.isnot(None),
            )
        )
        row = result.one()
        if row[1] and row[1] > 0:
            return float(row[0] / row[1])
        return 0.0

    async def get_credits_summary(self, student_id: int) -> dict:
        """Get credits summary for a student."""
        # Get earned credits (passed)
        earned_result = await self.session.execute(
            select(func.coalesce(func.sum(Subject.credits), 0))
            .select_from(Enrollment)
            .join(Group, Enrollment.group_id == Group.id)
            .join(Subject, Group.subject_id == Subject.id)
            .where(
                Enrollment.student_id == student_id,
                Enrollment.status == EnrollmentStatus.PASSED.value,
            )
        )
        earned = earned_result.scalar_one()

        # Get in-progress credits
        in_progress_result = await self.session.execute(
            select(func.coalesce(func.sum(Subject.credits), 0))
            .select_from(Enrollment)
            .join(Group, Enrollment.group_id == Group.id)
            .join(Subject, Group.subject_id == Subject.id)
            .where(
                Enrollment.student_id == student_id,
                Enrollment.status == EnrollmentStatus.ENROLLED.value,
            )
        )
        in_progress = in_progress_result.scalar_one()

        return {
            "earned": earned,
            "in_progress": in_progress,
            "total_attempted": earned + in_progress,
        }
