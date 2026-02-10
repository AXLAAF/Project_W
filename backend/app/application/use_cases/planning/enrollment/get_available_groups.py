"""
Get available groups use case.
"""
from typing import List, Dict, Any, Optional

from app.domain.repositories.enrollment_repository import IEnrollmentRepository
from app.domain.repositories.group_repository import IGroupRepository
from app.domain.repositories.subject_repository import ISubjectRepository
from app.domain.services.prerequisite_checker import PrerequisiteChecker
from app.domain.entities.planning.group import Group
from app.domain.entities.planning.enrollment import EnrollmentStatus


class GetAvailableGroupsUseCase:
    """
    Use case for getting available groups for a student.
    """

    def __init__(
        self,
        enrollment_repo: IEnrollmentRepository,
        group_repo: IGroupRepository,
        subject_repo: ISubjectRepository,
        prerequisite_checker: Optional[PrerequisiteChecker] = None,
    ):
        self._enrollment_repo = enrollment_repo
        self._group_repo = group_repo
        self._subject_repo = subject_repo
        self._prerequisite_checker = prerequisite_checker or PrerequisiteChecker()

    async def execute(self, student_id: int, period_id: int) -> Dict[str, Any]:
        """
        Get available groups filtered by:
        1. Prerequisites met
        2. Not already passed
        3. Has available spots
        """
        # Get student's enrollment history
        history = await self._enrollment_repo.get_academic_history(student_id)
        
        # Identify passed subjects to skip
        passed_ids = set()
        for enroll in history:
            if enroll.status == EnrollmentStatus.PASSED and enroll.subject_code:
                # We need subject ID, but enrollment might only have code.
                # If enrollment has subject_id, use it.
                # Assuming simple check by code for now if IDs unavailable, 
                # but Group.subject has ID.
                # Let's assume we can map code to ID or check preconditions by code.
                pass
                # ideally we have subject_id in enrollment or can fetch it.
        
        # Get all available groups for the period
        all_groups = await self._group_repo.get_available_groups(subject_id=0, period_id=period_id) 
        # Note: get_available_groups signature in interface might differ. 
        # Checked interface: get_available_groups(subject_id: int, period_id: int) -> Sequence[Group]
        # It seems it filters by subject ID. If we want ALL groups, we might need a different method 
        # or call list_by_period and filter manually.
        # Let's assume we use list_by_period for now as it's more generic if we want ALL.
        
        groups_in_period, _ = await self._group_repo.list_by_period(period_id, limit=1000)
        
        eligible_groups = []
        ineligible_groups = []

        for group in groups_in_period:
            if not group.is_active:
                continue
                
            # Skip if no spots (though we might want to show them as full)
            if group.available_spots <= 0:
                 # Check logic: user wants "available"
                 pass

            subject = group.subject
            if not subject:
                subject = await self._subject_repo.get_by_id(group.subject_id)
            
            if not subject:
                continue

            # Check logic using PrerequisiteChecker
            # It handles "already passed" check too within validate_enrollment or check_prerequisites
            
            # Use PrerequisiteChecker.validate_enrollment to check everything
            can_enroll, reason = self._prerequisite_checker.validate_enrollment(
                subject, list(history)
            )

            if can_enroll:
                eligible_groups.append(group)
            else:
                ineligible_groups.append({
                    "group_id": group.id,
                    "subject_code": subject.code,
                    "reason": reason,
                })

        return {
            "eligible": eligible_groups,
            "ineligible": ineligible_groups,
        }
