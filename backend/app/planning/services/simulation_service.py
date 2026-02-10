"""Simulation service for enrollment planning."""
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.planning.models.group import Schedule
from app.planning.repositories.group_repository import GroupRepository
from app.planning.repositories.enrollment_repository import EnrollmentRepository
from app.planning.services.subject_service import SubjectService
from app.planning.schemas.enrollment import (
    SimulationRequest,
    SimulationResult,
    ScheduleConflict,
)


class SimulationService:
    """Service for simulating enrollment scenarios."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.group_repo = GroupRepository(session)
        self.enrollment_repo = EnrollmentRepository(session)
        self.subject_service = SubjectService(session)

    async def simulate_enrollment(
        self, student_id: int, request: SimulationRequest
    ) -> SimulationResult:
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

        # Get student's passed subjects
        passed_ids = await self.enrollment_repo.get_passed_subjects(student_id)

        # Get all selected groups
        groups = []
        for group_id in request.group_ids:
            group = await self.group_repo.get_by_id(group_id)
            if group:
                groups.append(group)
            else:
                warnings.append(f"Group ID {group_id} not found")

        # Check each group
        for group in groups:
            total_credits += group.subject.credits

            # Check group capacity
            if group.is_full:
                warnings.append(f"{group.display_name} is full (waitlist)")
            elif group.available_spots <= 5:
                warnings.append(
                    f"{group.display_name} has only {group.available_spots} spots left"
                )

            # Check prerequisites
            prereq_met, missing = await self.subject_service.check_prerequisites_met(
                student_id, group.subject.id, passed_ids
            )
            if not prereq_met:
                for m in missing:
                    prerequisite_issues.append(
                        f"Missing prerequisite for {group.subject.code}: {m}"
                    )

        # Check schedule conflicts between all pairs of groups
        all_schedules = await self.group_repo.get_schedules_for_groups(request.group_ids)
        schedule_by_group = {}
        for schedule in all_schedules:
            if schedule.group_id not in schedule_by_group:
                schedule_by_group[schedule.group_id] = []
            schedule_by_group[schedule.group_id].append(schedule)

        # Compare schedules between groups
        group_list = list(schedule_by_group.keys())
        for i, group1_id in enumerate(group_list):
            for group2_id in group_list[i + 1:]:
                for sched1 in schedule_by_group[group1_id]:
                    for sched2 in schedule_by_group[group2_id]:
                        if sched1.overlaps_with(sched2):
                            conflicts.append(
                                ScheduleConflict(
                                    group1_id=group1_id,
                                    group2_id=group2_id,
                                    day=sched1.day_name,
                                    time_overlap=f"{sched1.time_range} ↔ {sched2.time_range}",
                                    message=f"Schedule conflict on {sched1.day_name}",
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

    async def get_available_groups_for_student(
        self, student_id: int, period_id: int
    ) -> dict:
        """
        Get available groups filtered by:
        1. Prerequisites met
        2. Not already passed
        3. Has available spots
        """
        # Get passed subjects
        passed_ids = await self.enrollment_repo.get_passed_subjects(student_id)

        # Get all available groups
        all_groups = await self.group_repo.get_available_groups(period_id)

        # Filter groups
        eligible_groups = []
        ineligible_groups = []

        for group in all_groups:
            subject_id = group.subject.id

            # Skip if already passed
            if subject_id in passed_ids:
                continue

            # Check prerequisites
            prereq_met, missing = await self.subject_service.check_prerequisites_met(
                student_id, subject_id, passed_ids
            )

            if prereq_met:
                eligible_groups.append(group)
            else:
                ineligible_groups.append({
                    "group": group,
                    "missing_prerequisites": missing,
                })

        return {
            "eligible": eligible_groups,
            "ineligible": ineligible_groups,
        }
