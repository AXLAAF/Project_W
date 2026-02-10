"""
SQLAlchemy implementation of Grade repository.
"""
from typing import Optional, Sequence, List
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.risk.partial_grade import PartialGrade
from app.domain.repositories.risk_repository import IGradeRepository
from app.infrastructure.persistence.sqlalchemy.risk_mappers import PartialGradeMapper
from app.risk.models.grade import PartialGrade as PartialGradeModel


class SQLAlchemyGradeRepository(IGradeRepository):
    """SQLAlchemy implementation of Grade repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, grade_id: int) -> Optional[PartialGrade]:
        """Get a grade by ID."""
        result = await self.session.execute(
            select(PartialGradeModel).where(PartialGradeModel.id == grade_id)
        )
        model = result.scalar_one_or_none()
        return PartialGradeMapper.to_entity(model) if model else None

    async def save(self, grade: PartialGrade) -> PartialGrade:
        """Save a new grade."""
        model = PartialGradeMapper.to_model(grade)
        self.session.add(model)
        await self.session.flush()
        return PartialGradeMapper.to_entity(model)

    async def update(self, grade: PartialGrade) -> PartialGrade:
        """Update an existing grade."""
        if grade.id is None:
            raise ValueError("Cannot update grade without ID")
            
        result = await self.session.execute(
            select(PartialGradeModel).where(PartialGradeModel.id == grade.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Grade with ID {grade.id} not found")
            
        PartialGradeMapper.update_model(model, grade)
        await self.session.flush()
        return PartialGradeMapper.to_entity(model)

    async def list_by_student(
        self,
        student_id: int,
        group_id: int,
    ) -> Sequence[PartialGrade]:
        """Get all grades for a student in a group."""
        result = await self.session.execute(
            select(PartialGradeModel)
            .where(
                PartialGradeModel.student_id == student_id,
                PartialGradeModel.group_id == group_id,
            )
            .order_by(PartialGradeModel.graded_at)
        )
        models = result.scalars().all()
        return [PartialGradeMapper.to_entity(model) for model in models]

    async def get_average(
        self,
        student_id: int,
        group_id: int,
    ) -> float:
        """Calculate weighted average grade for a student."""
        grades = await self.list_by_student(student_id, group_id)
        if not grades:
            return 0.0

        total_weight = sum(float(g.weight) for g in grades)
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(
            g.normalized_grade * float(g.weight) for g in grades
        )
        return weighted_sum / total_weight
