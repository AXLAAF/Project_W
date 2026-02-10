"""Group repository for database operations."""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.planning.models.group import Group, Schedule
from app.planning.models.academic_period import AcademicPeriod
from app.planning.schemas.group import GroupCreate, ScheduleCreate


class GroupRepository:
    """Repository for Group and Schedule operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: GroupCreate) -> Group:
        """Create a new group with schedules."""
        group = Group(
            subject_id=data.subject_id,
            period_id=data.period_id,
            professor_id=data.professor_id,
            group_number=data.group_number,
            capacity=data.capacity,
            classroom=data.classroom,
            modality=data.modality,
        )
        self.session.add(group)
        await self.session.flush()

        # Add schedules
        for schedule_data in data.schedules:
            schedule = Schedule(
                group_id=group.id,
                day_of_week=schedule_data.day_of_week,
                start_time=schedule_data.start_time,
                end_time=schedule_data.end_time,
                classroom=schedule_data.classroom or data.classroom,
                schedule_type=schedule_data.schedule_type,
            )
            self.session.add(schedule)

        return group

    async def get_by_id(self, group_id: int) -> Optional[Group]:
        """Get group by ID with schedules."""
        result = await self.session.execute(
            select(Group)
            .options(
                selectinload(Group.schedules),
                selectinload(Group.subject),
                selectinload(Group.professor),
            )
            .where(Group.id == group_id)
        )
        return result.scalar_one_or_none()

    async def get_by_subject_and_period(
        self,
        subject_id: int,
        period_id: int,
        is_active: bool = True,
    ) -> List[Group]:
        """Get all groups for a subject in a period."""
        result = await self.session.execute(
            select(Group)
            .options(selectinload(Group.schedules))
            .where(
                Group.subject_id == subject_id,
                Group.period_id == period_id,
                Group.is_active == is_active,
            )
            .order_by(Group.group_number)
        )
        return list(result.scalars().all())

    async def get_by_period(
        self,
        period_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Group]:
        """Get all groups for a period."""
        result = await self.session.execute(
            select(Group)
            .options(
                selectinload(Group.schedules),
                selectinload(Group.subject),
            )
            .where(Group.period_id == period_id, Group.is_active == True)
            .order_by(Group.subject_id, Group.group_number)
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_available_groups(
        self,
        period_id: int,
        subject_ids: Optional[List[int]] = None,
    ) -> List[Group]:
        """Get groups with available spots."""
        query = (
            select(Group)
            .options(
                selectinload(Group.schedules),
                selectinload(Group.subject),
            )
            .where(
                Group.period_id == period_id,
                Group.is_active == True,
                Group.enrolled_count < Group.capacity,
            )
        )

        if subject_ids:
            query = query.where(Group.subject_id.in_(subject_ids))

        result = await self.session.execute(query.order_by(Group.subject_id))
        return list(result.scalars().all())

    async def increment_enrolled(self, group_id: int) -> bool:
        """Increment enrolled count for a group."""
        group = await self.get_by_id(group_id)
        if group and not group.is_full:
            group.enrolled_count += 1
            return True
        return False

    async def decrement_enrolled(self, group_id: int) -> bool:
        """Decrement enrolled count for a group."""
        group = await self.get_by_id(group_id)
        if group and group.enrolled_count > 0:
            group.enrolled_count -= 1
            return True
        return False

    async def add_schedule(self, group_id: int, data: ScheduleCreate) -> Schedule:
        """Add a schedule to a group."""
        schedule = Schedule(
            group_id=group_id,
            day_of_week=data.day_of_week,
            start_time=data.start_time,
            end_time=data.end_time,
            classroom=data.classroom,
            schedule_type=data.schedule_type,
        )
        self.session.add(schedule)
        return schedule

    async def get_current_period(self) -> Optional[AcademicPeriod]:
        """Get the current academic period."""
        result = await self.session.execute(
            select(AcademicPeriod).where(AcademicPeriod.is_current == True)
        )
        return result.scalar_one_or_none()

    async def get_schedules_for_groups(self, group_ids: List[int]) -> List[Schedule]:
        """Get all schedules for a list of groups."""
        result = await self.session.execute(
            select(Schedule)
            .where(Schedule.group_id.in_(group_ids))
            .order_by(Schedule.day_of_week, Schedule.start_time)
        )
        return list(result.scalars().all())
