"""
SQLAlchemy implementation of ISubjectRepository.
"""
from typing import Optional, Sequence, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.domain.entities.planning.subject import Subject as SubjectEntity
from app.domain.repositories.subject_repository import ISubjectRepository
from app.infrastructure.persistence.sqlalchemy.planning_mappers import SubjectMapper
from app.planning.models.subject import Subject as SubjectModel, SubjectPrerequisite


class SQLAlchemySubjectRepository(ISubjectRepository):
    """SQLAlchemy implementation of subject repository."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def get_by_id(self, subject_id: int) -> Optional[SubjectEntity]:
        """Get a subject by ID."""
        stmt = (
            select(SubjectModel)
            .options(joinedload(SubjectModel.prerequisites).joinedload(SubjectPrerequisite.prerequisite))
            .where(SubjectModel.id == subject_id)
        )
        result = await self._session.execute(stmt)
        model = result.unique().scalar_one_or_none()
        
        if model is None:
            return None
        
        return SubjectMapper.to_entity(model)
    
    async def get_by_code(self, code: str) -> Optional[SubjectEntity]:
        """Get a subject by its code."""
        stmt = (
            select(SubjectModel)
            .options(joinedload(SubjectModel.prerequisites).joinedload(SubjectPrerequisite.prerequisite))
            .where(SubjectModel.code == code.upper())
        )
        result = await self._session.execute(stmt)
        model = result.unique().scalar_one_or_none()
        
        if model is None:
            return None
        
        return SubjectMapper.to_entity(model)
    
    async def save(self, subject: SubjectEntity) -> SubjectEntity:
        """Save a new subject."""
        model = SubjectMapper.to_model(subject)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        
        return SubjectMapper.to_entity(model)
    
    async def update(self, subject: SubjectEntity) -> SubjectEntity:
        """Update an existing subject."""
        stmt = select(SubjectModel).where(SubjectModel.id == subject.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model is None:
            raise ValueError(f"Subject with id {subject.id} not found")
        
        SubjectMapper.update_model(model, subject)
        await self._session.flush()
        await self._session.refresh(model)
        
        return SubjectMapper.to_entity(model)
    
    async def delete(self, subject_id: int) -> bool:
        """Delete a subject."""
        stmt = select(SubjectModel).where(SubjectModel.id == subject_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model is None:
            return False
        
        await self._session.delete(model)
        await self._session.flush()
        return True
    
    async def list_all(
        self,
        offset: int = 0,
        limit: int = 50,
        department: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[Sequence[SubjectEntity], int]:
        """List subjects with filtering and pagination."""
        # Base query
        stmt = (
            select(SubjectModel)
            .options(joinedload(SubjectModel.prerequisites).joinedload(SubjectPrerequisite.prerequisite))
        )
        count_stmt = select(func.count(SubjectModel.id))
        
        # Apply filters
        conditions = []
        
        if department:
            conditions.append(SubjectModel.department == department)
        
        if is_active is not None:
            conditions.append(SubjectModel.is_active == is_active)
        
        if search:
            search_pattern = f"%{search}%"
            conditions.append(
                or_(
                    SubjectModel.code.ilike(search_pattern),
                    SubjectModel.name.ilike(search_pattern),
                )
            )
        
        if conditions:
            stmt = stmt.where(*conditions)
            count_stmt = count_stmt.where(*conditions)
        
        # Get total count
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0
        
        # Apply pagination and ordering
        stmt = stmt.order_by(SubjectModel.code).offset(offset).limit(limit)
        
        result = await self._session.execute(stmt)
        models = result.unique().scalars().all()
        
        entities = [SubjectMapper.to_entity(m) for m in models]
        return entities, total
    
    async def get_prerequisites(self, subject_id: int) -> Sequence[SubjectEntity]:
        """Get all prerequisites for a subject."""
        stmt = (
            select(SubjectModel)
            .join(SubjectPrerequisite, SubjectPrerequisite.prerequisite_id == SubjectModel.id)
            .where(SubjectPrerequisite.subject_id == subject_id)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        
        return [SubjectMapper.to_entity(m) for m in models]
    
    async def get_available_for_student(
        self,
        student_id: int,
        period_id: int,
    ) -> Sequence[SubjectEntity]:
        """Get subjects available for a student to enroll in."""
        # This requires more complex logic with enrollment checking
        # For now, return all active subjects
        # The actual filtering should be done in the use case layer
        stmt = (
            select(SubjectModel)
            .options(joinedload(SubjectModel.prerequisites).joinedload(SubjectPrerequisite.prerequisite))
            .where(SubjectModel.is_active == True)
            .order_by(SubjectModel.code)
        )
        result = await self._session.execute(stmt)
        models = result.unique().scalars().all()
        
        return [SubjectMapper.to_entity(m) for m in models]
