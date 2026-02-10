"""
SQLAlchemy implementation of Risk Assessment repository.
"""
from typing import Optional, Sequence, List
from datetime import datetime, timedelta

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.risk.risk_assessment import RiskAssessment
from app.domain.repositories.risk_repository import IRiskAssessmentRepository
from app.domain.value_objects.risk import RiskLevel
from app.infrastructure.persistence.sqlalchemy.risk_mappers import RiskAssessmentMapper
from app.risk.models.risk_assessment import RiskAssessment as RiskAssessmentModel
from app.core.models.user import User  # Needed for relationship loading if applicable


class SQLAlchemyRiskAssessmentRepository(IRiskAssessmentRepository):
    """SQLAlchemy implementation of Risk Assessment repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, assessment_id: int) -> Optional[RiskAssessment]:
        """Get a risk assessment by ID."""
        result = await self.session.execute(
            select(RiskAssessmentModel).where(RiskAssessmentModel.id == assessment_id)
        )
        model = result.scalar_one_or_none()
        return RiskAssessmentMapper.to_entity(model) if model else None

    async def save(self, assessment: RiskAssessment) -> RiskAssessment:
        """Save a new risk assessment."""
        model = RiskAssessmentMapper.to_model(assessment)
        self.session.add(model)
        await self.session.flush()  # To get ID
        return RiskAssessmentMapper.to_entity(model)

    async def get_latest(self, student_id: int, group_id: int) -> Optional[RiskAssessment]:
        """Get the latest risk assessment for a student in a group."""
        result = await self.session.execute(
            select(RiskAssessmentModel)
            .where(
                RiskAssessmentModel.student_id == student_id,
                RiskAssessmentModel.group_id == group_id,
            )
            .order_by(RiskAssessmentModel.assessed_at.desc())
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return RiskAssessmentMapper.to_entity(model) if model else None

    async def get_at_risk_students(
        self,
        group_id: int,
        min_level: RiskLevel = RiskLevel.HIGH,
    ) -> Sequence[RiskAssessment]:
        """Get students at or above a risk level in a group."""
        levels = [RiskLevel.CRITICAL.value]
        if min_level in (RiskLevel.HIGH, RiskLevel.MEDIUM, RiskLevel.LOW):
            levels.append(RiskLevel.HIGH.value)
        if min_level in (RiskLevel.MEDIUM, RiskLevel.LOW):
            levels.append(RiskLevel.MEDIUM.value)
        if min_level == RiskLevel.LOW:
            levels.append(RiskLevel.LOW.value)

        # Get latest assessment per student
        subquery = (
            select(
                RiskAssessmentModel.student_id,
                func.max(RiskAssessmentModel.assessed_at).label("max_date"),
            )
            .where(RiskAssessmentModel.group_id == group_id)
            .group_by(RiskAssessmentModel.student_id)
            .subquery()
        )

        result = await self.session.execute(
            select(RiskAssessmentModel)
            .join(
                subquery,
                and_(
                    RiskAssessmentModel.student_id == subquery.c.student_id,
                    RiskAssessmentModel.assessed_at == subquery.c.max_date,
                ),
            )
            .where(
                RiskAssessmentModel.group_id == group_id,
                RiskAssessmentModel.risk_level.in_(levels),
            )
            .order_by(RiskAssessmentModel.risk_score.desc())
        )
        models = result.scalars().all()
        return [RiskAssessmentMapper.to_entity(model) for model in models]

    async def get_history(
        self,
        student_id: int,
        group_id: int,
        days: int = 30,
    ) -> Sequence[RiskAssessment]:
        """Get risk assessment history for a student."""
        since = datetime.now() - timedelta(days=days)
        result = await self.session.execute(
            select(RiskAssessmentModel)
            .where(
                RiskAssessmentModel.student_id == student_id,
                RiskAssessmentModel.group_id == group_id,
                RiskAssessmentModel.assessed_at >= since,
            )
            .order_by(RiskAssessmentModel.assessed_at)
        )
        models = result.scalars().all()
        return [RiskAssessmentMapper.to_entity(model) for model in models]
