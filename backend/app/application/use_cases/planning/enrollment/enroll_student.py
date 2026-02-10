"""
Enroll student use case.
Application layer orchestration for enrolling a student in a group.
"""
from dataclasses import dataclass
from typing import Optional, List

from app.domain.repositories.enrollment_repository import IEnrollmentRepository
from app.domain.repositories.group_repository import IGroupRepository
from app.domain.repositories.subject_repository import ISubjectRepository
from app.domain.services.prerequisite_checker import PrerequisiteChecker
from app.domain.services.schedule_conflict_detector import ScheduleConflictDetector
from app.domain.entities.planning.enrollment import Enrollment, EnrollmentStatus


@dataclass
class EnrollmentResultDTO:
    """Result of enrollment attempt."""
    success: bool
    enrollment_id: Optional[int] = None
    error_message: Optional[str] = None
    conflict_details: Optional[list] = None


class EnrollStudentUseCase:
    """
    Use case for enrolling a student in a course group.
    
    Orchestrates:
    - Prerequisite validation
    - Schedule conflict detection
    - Group capacity check
    - Enrollment creation
    """
    
    def __init__(
        self,
        enrollment_repo: IEnrollmentRepository,
        group_repo: IGroupRepository,
        subject_repo: ISubjectRepository,
        prerequisite_checker: Optional[PrerequisiteChecker] = None,
        conflict_detector: Optional[ScheduleConflictDetector] = None,
    ):
        self._enrollment_repo = enrollment_repo
        self._group_repo = group_repo
        self._subject_repo = subject_repo
        self._prerequisite_checker = prerequisite_checker or PrerequisiteChecker()
        self._conflict_detector = conflict_detector or ScheduleConflictDetector()
    
    async def execute(
        self,
        student_id: int,
        group_id: int,
        skip_prerequisite_check: bool = False,
        skip_conflict_check: bool = False,
    ) -> EnrollmentResultDTO:
        """
        Enroll a student in a group.
        
        Args:
            student_id: ID of the student
            group_id: ID of the group to enroll in
            skip_prerequisite_check: Admin override for prerequisites
            skip_conflict_check: Admin override for conflicts
        
        Returns:
            EnrollmentResultDTO with success status and details
        """
        # 1. Get the group
        group = await self._group_repo.get_by_id(group_id)
        if not group:
            return EnrollmentResultDTO(
                success=False,
                error_message="Group not found",
            )
        
        # 2. Check if group is active and has capacity
        if not group.can_enroll():
            if not group.is_active:
                return EnrollmentResultDTO(
                    success=False,
                    error_message="Group is not active",
                )
            return EnrollmentResultDTO(
                success=False,
                error_message="Group is at full capacity",
            )
        
        # 3. Check if already enrolled in this group
        existing = await self._enrollment_repo.get_by_student_and_group(student_id, group_id)
        if existing and existing.status == EnrollmentStatus.ENROLLED:
            return EnrollmentResultDTO(
                success=False,
                error_message="Already enrolled in this group",
            )
        
        # 4. Get subject and check prerequisites
        if not skip_prerequisite_check:
            subject = await self._subject_repo.get_by_id(group.subject_id)
            if subject:
                history = await self._enrollment_repo.get_academic_history(student_id)
                can_enroll, reason = self._prerequisite_checker.validate_enrollment(
                    subject, list(history)
                )
                if not can_enroll:
                    return EnrollmentResultDTO(
                        success=False,
                        error_message=reason,
                    )
        
        # 5. Check schedule conflicts
        if not skip_conflict_check:
            current_enrollments = await self._enrollment_repo.get_current_enrollments(student_id)
            enrolled_groups = []
            for enroll in current_enrollments:
                enrolled_group = await self._group_repo.get_by_id(enroll.group_id)
                if enrolled_group:
                    enrolled_groups.append(enrolled_group)
            
            if self._conflict_detector.has_conflict(group, enrolled_groups):
                conflicts = self._conflict_detector.get_conflict_details(group, enrolled_groups)
                return EnrollmentResultDTO(
                    success=False,
                    error_message="Schedule conflict detected",
                    conflict_details=conflicts,
                )
        
        # 6. Determine attempt number
        attempt_count = await self._enrollment_repo.count_attempts(student_id, group.subject_id)
        
        # 7. Create enrollment
        enrollment = Enrollment.create(
            student_id=student_id,
            group_id=group_id,
            subject_code=group.subject_code,
            subject_name=group.subject_name,
            attempt_number=attempt_count + 1,
        )
        
        saved = await self._enrollment_repo.save(enrollment)
        
        # 8. Update group enrolled count
        await self._group_repo.increment_enrolled(group_id)
        
        return EnrollmentResultDTO(
            success=True,
            enrollment_id=saved.id,
        )
