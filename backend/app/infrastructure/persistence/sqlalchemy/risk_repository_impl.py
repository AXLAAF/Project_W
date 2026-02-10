"""
SQLAlchemy implementation of Risk Repository.
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.risk_repository import IRiskRepository
from app.domain.entities.risk.risk_assessment import RiskAssessment, RiskLevel
from app.risk.models.risk_assessment import RiskAssessment as RiskModel


class SQLAlchemyRiskRepository(IRiskRepository):
    """SQLAlchemy implementation of risk repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, assessment: RiskAssessment) -> RiskAssessment:
        if assessment.id:
            return await self._update(assessment)
        return await self._create(assessment)

    async def _create(self, assessment: RiskAssessment) -> RiskAssessment:
        model = RiskModel(
            student_id=assessment.student_id,
            group_id=assessment.group_id,
            risk_score=assessment.risk_score,
            risk_level=assessment.risk_level.value,
            attendance_score=assessment.attendance_score,
            grades_score=assessment.grades_score,
            assignments_score=assessment.assignments_score,
            factor_details=assessment.factor_details,
            recommendation=assessment.recommendation,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def _update(self, assessment: RiskAssessment) -> RiskAssessment:
        stmt = select(RiskModel).where(RiskModel.id == assessment.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError(f"Risk assessment {assessment.id} not found")
            
        model.risk_score = assessment.risk_score
        model.risk_level = assessment.risk_level.value
        model.attendance_score = assessment.attendance_score
        model.grades_score = assessment.grades_score
        model.assignments_score = assessment.assignments_score
        model.factor_details = assessment.factor_details
        model.recommendation = assessment.recommendation
        
        await self.session.flush()
        return self._to_entity(model)

    async def get_by_student_and_group(self, student_id: int, group_id: int) -> Optional[RiskAssessment]:
        stmt = (
            select(RiskModel)
            .where(RiskModel.student_id == student_id, RiskModel.group_id == group_id)
            .order_by(RiskModel.assessed_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_history_by_student(self, student_id: int, limit: int = 10) -> List[RiskAssessment]:
        stmt = (
            select(RiskModel)
            .where(RiskModel.student_id == student_id)
            .order_by(RiskModel.assessed_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_high_risk_students(self, group_id: int) -> List[RiskAssessment]:
        stmt = (
            select(RiskModel)
            .where(
                RiskModel.group_id == group_id,
                RiskModel.risk_level.in_([RiskLevel.HIGH.value, RiskLevel.CRITICAL.value])
            )
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    def _to_entity(self, model: RiskModel) -> RiskAssessment:
        return RiskAssessment(
            id=model.id,
            student_id=model.student_id,
            group_id=model.group_id,
            risk_score=model.risk_score,
            risk_level=RiskLevel(model.risk_level),
            attendance_score=model.attendance_score,
            grades_score=model.grades_score,
            assignments_score=model.assignments_score,
            factor_details=model.factor_details or {},
            recommendation=model.recommendation,
            assessed_at=model.assessed_at,
            created_at=model.created_at
        )
