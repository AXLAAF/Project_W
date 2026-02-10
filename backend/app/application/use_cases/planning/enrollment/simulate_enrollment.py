"""
Simulate enrollment use case.
"""
from typing import List, Dict, Any, Optional

from app.domain.repositories.enrollment_repository import IEnrollmentRepository
from app.domain.repositories.group_repository import IGroupRepository
from app.domain.repositories.subject_repository import ISubjectRepository
from app.domain.services.prerequisite_checker import PrerequisiteChecker
from app.domain.services.schedule_conflict_detector import ScheduleConflictDetector
from app.domain.entities.planning.enrollment import EnrollmentStatus
from app.planning.schemas.enrollment import SimulationRequest, SimulationResult, ScheduleConflict


class SimulateEnrollmentUseCase:
    """
    Use case for simulating an enrollment scenario.
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

    async def execute(self, student_id: int, request: SimulationRequest) -> SimulationResult:
        """
        Simulate an enrollment scenario to detect conflicts and issues.
        
        Checks:
        1. Schedule conflicts between selected groups
        2. Prerequisites for each subject
        3. Group capacity
        4. Maximum credits per semester
        """
        conflicts: List[ScheduleConflict] = []
        prerequisite_issues: List[str] = []
        warnings: List[str] = []
        total_credits = 0

        # Get student's enrollment history to check passed subjects
        history = await self._enrollment_repo.get_academic_history(student_id)
        # Passed enrollments are needed for prerequisite check
        # PrerequisiteChecker expects generic "Enrollment" entities or similar interface
        
        # Get all selected groups
        groups = []
        for group_id in request.group_ids:
            group = await self._group_repo.get_by_id(group_id)
            if group:
                groups.append(group)
            else:
                warnings.append(f"Group ID {group_id} not found")

        # Check each group
        for group in groups:
            # Load subject (needed for credits and prerequisites)
            # Assuming group has subject loaded, or we fetch it
            subject = group.subject
            if not subject:
                # If subject not loaded in group, fetch it
                subject = await self._subject_repo.get_by_id(group.subject_id)
                # Assign to group for convenience if possible, or just use it
            
            if subject:
                total_credits += subject.credits

                # Check prerequisites
                # We need to pass the FULL subject entity with prerequisites loaded to the checker
                # Ensure subject has prerequisites loaded. 
                # If repo.get_by_id doesn't load them, we might need a specific method.
                # Assuming standard repo loads aggregates or we trust what we have.
                
                can_enroll, missing = self._prerequisite_checker.check_prerequisites(
                    subject, list(history)
                )
                if not can_enroll:
                    for m in missing:
                        prerequisite_issues.append(
                            f"Missing prerequisite for {subject.code}: {m}"
                        )
            
            # Check group capacity
            if group.is_full:
                warnings.append(f"Group {group.group_number} ({subject.name if subject else 'Unknown'}) is full")
            elif group.available_spots <= 5:
                warnings.append(
                    f"Group {group.group_number} ({subject.name if subject else 'Unknown'}) has only {group.available_spots} spots left"
                )

        # Check schedule conflicts between selected groups
        detected_conflicts = self._conflict_detector.detect_conflicts(groups)
        for g1, g2, s1, s2 in detected_conflicts:
            conflicts.append(
                ScheduleConflict(
                    group1_id=g1.id,
                    group2_id=g2.id,
                    day=s1.day_name, # Assuming day_name property exists or we map enum
                    time_overlap=f"{s1.start_time}-{s1.end_time} <-> {s2.start_time}-{s2.end_time}",
                    message=f"Conflict between {g1.group_number} and {g2.group_number} on {s1.day_name}",
                )
            )

        # Check credit limits
        if total_credits > 24:
            warnings.append(
                f"Total credits ({total_credits}) exceeds recommended maximum (24)"
            )
        elif total_credits > 21:
            warnings.append(
                f"High credit load ({total_credits} credits)"
            )

        is_valid = len(conflicts) == 0 and len(prerequisite_issues) == 0

        return SimulationResult(
            is_valid=is_valid,
            total_credits=total_credits,
            conflicts=conflicts,
            prerequisite_issues=prerequisite_issues,
            warnings=warnings,
        )
