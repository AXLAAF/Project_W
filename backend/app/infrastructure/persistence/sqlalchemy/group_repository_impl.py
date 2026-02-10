"""
SQLAlchemy implementation of IGroupRepository.
"""
from typing import Optional, Sequence, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.domain.entities.planning.group import Group as GroupEntity
from app.domain.repositories.group_repository import IGroupRepository
from app.infrastructure.persistence.sqlalchemy.planning_mappers import GroupMapper, ScheduleMapper
from app.planning.models.group import Group as GroupModel, Schedule as ScheduleModel


class SQLAlchemyGroupRepository(IGroupRepository):
    """SQLAlchemy implementation of group repository."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def get_by_id(self, group_id: int) -> Optional[GroupEntity]:
        """Get a group by ID."""
        stmt = (
            select(GroupModel)
            .options(
                joinedload(GroupModel.subject),
                joinedload(GroupModel.period),
                joinedload(GroupModel.professor).joinedload("profile"),
                joinedload(GroupModel.schedules),
            )
            .where(GroupModel.id == group_id)
        )
        result = await self._session.execute(stmt)
        model = result.unique().scalar_one_or_none()
        
        if model is None:
            return None
        
        return GroupMapper.to_entity(model)
    
    async def save(self, group: GroupEntity) -> GroupEntity:
        """Save a new group."""
        model = GroupMapper.to_model(group)
        self._session.add(model)
        await self._session.flush()
        
        # Add schedules
        for schedule in group.schedules:
            schedule_model = ScheduleMapper.to_model(schedule, model.id)
            self._session.add(schedule_model)
        
        await self._session.flush()
        await self._session.refresh(model)
        
        # Reload with relationships
        return await self.get_by_id(model.id)
    
    async def update(self, group: GroupEntity) -> GroupEntity:
        """Update an existing group."""
        stmt = select(GroupModel).where(GroupModel.id == group.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model is None:
            raise ValueError(f"Group with id {group.id} not found")
        
        GroupMapper.update_model(model, group)
        await self._session.flush()
        
        return await self.get_by_id(model.id)
    
    async def delete(self, group_id: int) -> bool:
        """Delete a group."""
        stmt = select(GroupModel).where(GroupModel.id == group_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model is None:
            return False
        
        await self._session.delete(model)
        await self._session.flush()
        return True
    
    async def list_by_subject(
        self,
        subject_id: int,
        period_id: Optional[int] = None,
        is_active: bool = True,
    ) -> Sequence[GroupEntity]:
        """Get all groups for a subject, optionally filtered by period."""
        stmt = (
            select(GroupModel)
            .options(
                joinedload(GroupModel.subject),
                joinedload(GroupModel.period),
                joinedload(GroupModel.professor).joinedload("profile"),
                joinedload(GroupModel.schedules),
            )
            .where(GroupModel.subject_id == subject_id)
            .where(GroupModel.is_active == is_active)
        )
        
        if period_id:
            stmt = stmt.where(GroupModel.period_id == period_id)
        
        stmt = stmt.order_by(GroupModel.group_number)
        
        result = await self._session.execute(stmt)
        models = result.unique().scalars().all()
        
        return [GroupMapper.to_entity(m) for m in models]
    
    async def list_by_period(
        self,
        period_id: int,
        offset: int = 0,
        limit: int = 50,
    ) -> Tuple[Sequence[GroupEntity], int]:
        """Get all groups in an academic period."""
        # Count query
        count_stmt = (
            select(func.count(GroupModel.id))
            .where(GroupModel.period_id == period_id)
        )
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0
        
        # Data query
        stmt = (
            select(GroupModel)
            .options(
                joinedload(GroupModel.subject),
                joinedload(GroupModel.period),
                joinedload(GroupModel.professor).joinedload("profile"),
                joinedload(GroupModel.schedules),
            )
            .where(GroupModel.period_id == period_id)
            .order_by(GroupModel.subject_id, GroupModel.group_number)
            .offset(offset)
            .limit(limit)
        )
        
        result = await self._session.execute(stmt)
        models = result.unique().scalars().all()
        
        entities = [GroupMapper.to_entity(m) for m in models]
        return entities, total
    
    async def list_by_professor(
        self,
        professor_id: int,
        period_id: Optional[int] = None,
    ) -> Sequence[GroupEntity]:
        """Get all groups taught by a professor."""
        stmt = (
            select(GroupModel)
            .options(
                joinedload(GroupModel.subject),
                joinedload(GroupModel.period),
                joinedload(GroupModel.schedules),
            )
            .where(GroupModel.professor_id == professor_id)
            .where(GroupModel.is_active == True)
        )
        
        if period_id:
            stmt = stmt.where(GroupModel.period_id == period_id)
        
        stmt = stmt.order_by(GroupModel.subject_id, GroupModel.group_number)
        
        result = await self._session.execute(stmt)
        models = result.unique().scalars().all()
        
        return [GroupMapper.to_entity(m) for m in models]
    
    async def get_available_groups(
        self,
        subject_id: int,
        period_id: int,
    ) -> Sequence[GroupEntity]:
        """Get groups with available spots for enrollment."""
        stmt = (
            select(GroupModel)
            .options(
                joinedload(GroupModel.subject),
                joinedload(GroupModel.period),
                joinedload(GroupModel.professor).joinedload("profile"),
                joinedload(GroupModel.schedules),
            )
            .where(GroupModel.subject_id == subject_id)
            .where(GroupModel.period_id == period_id)
            .where(GroupModel.is_active == True)
            .where(GroupModel.enrolled_count < GroupModel.capacity)
            .order_by(GroupModel.group_number)
        )
        
        result = await self._session.execute(stmt)
        models = result.unique().scalars().all()
        
        return [GroupMapper.to_entity(m) for m in models]
    
    async def increment_enrolled(self, group_id: int) -> bool:
        """Increment enrolled count for a group."""
        stmt = select(GroupModel).where(GroupModel.id == group_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model is None:
            return False
        
        if model.enrolled_count >= model.capacity:
            return False
        
        model.enrolled_count += 1
        await self._session.flush()
        return True
    
    async def decrement_enrolled(self, group_id: int) -> bool:
        """Decrement enrolled count for a group."""
        stmt = select(GroupModel).where(GroupModel.id == group_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model is None:
            return False
        
        if model.enrolled_count > 0:
            model.enrolled_count -= 1
        
        await self._session.flush()
        return True
