"""
SQLAlchemy implementation of IEnrollmentRepository.
"""
from typing import Optional, Sequence

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.domain.entities.planning.enrollment import Enrollment as EnrollmentEntity, EnrollmentStatus as DomainEnrollmentStatus
from app.domain.repositories.enrollment_repository import IEnrollmentRepository
from app.infrastructure.persistence.sqlalchemy.planning_mappers import EnrollmentMapper
from app.planning.models.enrollment import Enrollment as EnrollmentModel, EnrollmentStatus as ORMEnrollmentStatus
from app.planning.models.group import Group as GroupModel


class SQLAlchemyEnrollmentRepository(IEnrollmentRepository):
    """SQLAlchemy implementation of enrollment repository."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def get_by_id(self, enrollment_id: int) -> Optional[EnrollmentEntity]:
        """Get an enrollment by ID."""
        stmt = (
            select(EnrollmentModel)
            .options(
                joinedload(EnrollmentModel.group).joinedload(GroupModel.subject),
                joinedload(EnrollmentModel.student),
            )
            .where(EnrollmentModel.id == enrollment_id)
        )
        result = await self._session.execute(stmt)
        model = result.unique().scalar_one_or_none()
        
        if model is None:
            return None
        
        return EnrollmentMapper.to_entity(model)
    
    async def save(self, enrollment: EnrollmentEntity) -> EnrollmentEntity:
        """Save a new enrollment."""
        model = EnrollmentMapper.to_model(enrollment)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        
        # Reload with relationships
        return await self.get_by_id(model.id)
    
    async def update(self, enrollment: EnrollmentEntity) -> EnrollmentEntity:
        """Update an existing enrollment."""
        stmt = select(EnrollmentModel).where(EnrollmentModel.id == enrollment.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model is None:
            raise ValueError(f"Enrollment with id {enrollment.id} not found")
        
        EnrollmentMapper.update_model(model, enrollment)
        await self._session.flush()
        
        return await self.get_by_id(model.id)
    
    async def delete(self, enrollment_id: int) -> bool:
        """Delete an enrollment."""
        stmt = select(EnrollmentModel).where(EnrollmentModel.id == enrollment_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model is None:
            return False
        
        await self._session.delete(model)
        await self._session.flush()
        return True
    
    async def get_by_student_and_group(
        self,
        student_id: int,
        group_id: int,
    ) -> Optional[EnrollmentEntity]:
        """Get enrollment for a specific student in a specific group."""
        stmt = (
            select(EnrollmentModel)
            .options(
                joinedload(EnrollmentModel.group).joinedload(GroupModel.subject),
            )
            .where(
                and_(
                    EnrollmentModel.student_id == student_id,
                    EnrollmentModel.group_id == group_id,
                )
            )
        )
        result = await self._session.execute(stmt)
        model = result.unique().scalar_one_or_none()
        
        if model is None:
            return None
        
        return EnrollmentMapper.to_entity(model)
    
    async def list_by_student(
        self,
        student_id: int,
        status: Optional[DomainEnrollmentStatus] = None,
        period_id: Optional[int] = None,
    ) -> Sequence[EnrollmentEntity]:
        """Get all enrollments for a student."""
        stmt = (
            select(EnrollmentModel)
            .options(
                joinedload(EnrollmentModel.group).joinedload(GroupModel.subject),
                joinedload(EnrollmentModel.group).joinedload(GroupModel.period),
            )
            .where(EnrollmentModel.student_id == student_id)
        )
        
        if status:
            stmt = stmt.where(EnrollmentModel.status == status.value)
        
        if period_id:
            stmt = stmt.join(GroupModel).where(GroupModel.period_id == period_id)
        
        stmt = stmt.order_by(EnrollmentModel.enrolled_at.desc())
        
        result = await self._session.execute(stmt)
        models = result.unique().scalars().all()
        
        return [EnrollmentMapper.to_entity(m) for m in models]
    
    async def list_by_group(
        self,
        group_id: int,
        status: Optional[DomainEnrollmentStatus] = None,
    ) -> Sequence[EnrollmentEntity]:
        """Get all enrollments in a group."""
        stmt = (
            select(EnrollmentModel)
            .options(
                joinedload(EnrollmentModel.student).joinedload("profile"),
                joinedload(EnrollmentModel.group).joinedload(GroupModel.subject),
            )
            .where(EnrollmentModel.group_id == group_id)
        )
        
        if status:
            stmt = stmt.where(EnrollmentModel.status == status.value)
        
        stmt = stmt.order_by(EnrollmentModel.enrolled_at)
        
        result = await self._session.execute(stmt)
        models = result.unique().scalars().all()
        
        return [EnrollmentMapper.to_entity(m) for m in models]
    
    async def get_academic_history(
        self,
        student_id: int,
    ) -> Sequence[EnrollmentEntity]:
        """Get complete academic history for a student."""
        stmt = (
            select(EnrollmentModel)
            .options(
                joinedload(EnrollmentModel.group).joinedload(GroupModel.subject),
                joinedload(EnrollmentModel.group).joinedload(GroupModel.period),
            )
            .where(EnrollmentModel.student_id == student_id)
            .order_by(EnrollmentModel.enrolled_at.desc())
        )
        
        result = await self._session.execute(stmt)
        models = result.unique().scalars().all()
        
        return [EnrollmentMapper.to_entity(m) for m in models]
    
    async def get_current_enrollments(
        self,
        student_id: int,
    ) -> Sequence[EnrollmentEntity]:
        """Get current active enrollments for a student."""
        stmt = (
            select(EnrollmentModel)
            .options(
                joinedload(EnrollmentModel.group).joinedload(GroupModel.subject),
                joinedload(EnrollmentModel.group).joinedload(GroupModel.schedules),
            )
            .where(
                and_(
                    EnrollmentModel.student_id == student_id,
                    EnrollmentModel.status == ORMEnrollmentStatus.ENROLLED.value,
                )
            )
        )
        
        result = await self._session.execute(stmt)
        models = result.unique().scalars().all()
        
        return [EnrollmentMapper.to_entity(m) for m in models]
    
    async def count_attempts(
        self,
        student_id: int,
        subject_id: int,
    ) -> int:
        """Count how many times a student has attempted a subject."""
        stmt = (
            select(func.count(EnrollmentModel.id))
            .join(GroupModel)
            .where(
                and_(
                    EnrollmentModel.student_id == student_id,
                    GroupModel.subject_id == subject_id,
                )
            )
        )
        
        result = await self._session.execute(stmt)
        return result.scalar() or 0
    
    async def has_passed_subject(
        self,
        student_id: int,
        subject_id: int,
    ) -> bool:
        """Check if student has passed a specific subject."""
        stmt = (
            select(EnrollmentModel.id)
            .join(GroupModel)
            .where(
                and_(
                    EnrollmentModel.student_id == student_id,
                    GroupModel.subject_id == subject_id,
                    EnrollmentModel.status == ORMEnrollmentStatus.PASSED.value,
                )
            )
            .limit(1)
        )
        
        result = await self._session.execute(stmt)
        return result.scalar() is not None
