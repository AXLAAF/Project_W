"""
List Groups Use Case.
"""
from typing import List, Optional, Tuple

from app.domain.repositories.group_repository import IGroupRepository
from app.domain.repositories.period_repository import IPeriodRepository
from app.application.dtos.planning_dtos import GroupDTO, ScheduleDTO
from app.domain.entities.planning.group import Group

class ListGroupsUseCase:
    def __init__(
        self,
        group_repo: IGroupRepository,
        period_repo: IPeriodRepository,
    ):
        self.group_repo = group_repo
        self.period_repo = period_repo

    async def execute(
        self,
        period_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Tuple[List[GroupDTO], int]:
        
        # Determine period
        current_period = None
        if period_id is None:
            current_period = await self.period_repo.get_current_period()
            if current_period:
                period_id = current_period.id
        
        # If still no period and no subject filter, likely return empty or all active?
        # Legacy logic: if no period, return empty list (unless subject filtered?)
        # Legacy: if subject_id and period_id, list_by_subject (implementation filtered).
        # Legacy: if period_id, list_by_period.
        # Legacy: if no period, try current. if no current, return empty.

        groups = []
        total = 0

        if subject_id and period_id:
             # list_by_subject usually returns all groups for subject/period
             # Pagination might not be supported by list_by_subject in repo interface?
             # Checking repo interface: list_by_subject returns Sequence[Group] (no total, no offset/limit in interface I saw).
             # Let's assume for now it returns all. Or we slice in memory if needed (not efficient but safe).
             # But if limit is 500, unlikely to have >500 groups for one subject.
             groups = await self.group_repo.list_by_subject(subject_id, period_id)
             # Manually slice if needed or just return all
             total = len(groups)
             # Slice
             groups = groups[offset : offset + limit]
        
        elif period_id:
            groups, total = await self.group_repo.list_by_period(period_id, offset, limit)
        
        else:
            # No period found/specified and no subject specified
            return [], 0

        dtos = [self._to_dto(g) for g in groups]
        return dtos, total

    def _to_dto(self, group: Group) -> GroupDTO:
        schedule_dtos = [
            ScheduleDTO(
                id=s.id,
                group_id=group.id,
                day_of_week=s.day_of_week.value if hasattr(s.day_of_week, 'value') else s.day_of_week,
                start_time=s.start_time,
                end_time=s.end_time,
                classroom=s.classroom,
                schedule_type=s.schedule_type,
                day_name=getattr(s, 'day_name', ''), # Property might strictly need object
                time_range=getattr(s, 'time_range', ''),
            ) for s in group.schedules
        ]
        
        return GroupDTO(
            id=group.id,
            code=group.group_number,
            subject_id=group.subject_id,
            academic_period_id=group.period_id,
            teacher_id=group.professor_id,
            quota=group.capacity,
            enrolled_count=group.enrolled_count,
            available_spots=group.available_spots,
            is_full=group.is_full,
            schedule_summary=None, # Could compute from schedules
            is_active=group.is_active,
            subject_code=group.subject_code or "",
            subject_name=group.subject_name or "",
            teacher_name=group.professor_name,
            schedules=schedule_dtos
        )
