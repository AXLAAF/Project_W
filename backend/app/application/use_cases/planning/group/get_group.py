"""
Get Group Use Case.
"""
from app.domain.repositories.group_repository import IGroupRepository
from app.application.dtos.planning_dtos import GroupDTO, ScheduleDTO
from app.domain.entities.planning.group import Group

class GetGroupUseCase:
    def __init__(self, group_repo: IGroupRepository):
        self.group_repo = group_repo

    async def execute(self, group_id: int) -> GroupDTO:
        group = await self.group_repo.get_by_id(group_id)
        if not group:
            raise ValueError(f"Group with ID {group_id} not found")
        
        return self._to_dto(group)

    def _to_dto(self, group: Group) -> GroupDTO:
        # Duplicated mapping logic - ideally shared
        schedule_dtos = [
            ScheduleDTO(
                id=s.id,
                group_id=group.id,
                day_of_week=s.day_of_week.value if hasattr(s.day_of_week, 'value') else s.day_of_week,
                start_time=s.start_time,
                end_time=s.end_time,
                classroom=s.classroom,
                schedule_type=s.schedule_type,
                day_name=getattr(s, 'day_name', ''),
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
            schedule_summary=None,
            is_active=group.is_active,
            subject_code=group.subject_code or "",
            subject_name=group.subject_name or "",
            teacher_name=group.professor_name,
            schedules=schedule_dtos
        )
