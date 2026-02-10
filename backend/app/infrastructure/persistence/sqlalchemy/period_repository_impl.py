"""
SQLAlchemy implementation of IPeriodRepository.
"""
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.planning.academic_period import AcademicPeriod
from app.domain.repositories.period_repository import IPeriodRepository
from app.planning.models.academic_period import AcademicPeriod as PeriodModel

# Need mapper if not using model directly. 
# Assuming Mapper exists or I create simple mapper here.
# Let's check planning_mappers.py later, but for now simple conversion.

class SQLAlchemyPeriodRepository(IPeriodRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_current_period(self) -> Optional[AcademicPeriod]:
        stmt = (
            select(PeriodModel)
            .where(PeriodModel.is_active == True)
            .order_by(PeriodModel.start_date.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_id(self, period_id: int) -> Optional[AcademicPeriod]:
        stmt = select(PeriodModel).where(PeriodModel.id == period_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(self) -> List[AcademicPeriod]:
        stmt = select(PeriodModel).order_by(PeriodModel.start_date.desc())
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    def _to_entity(self, model: PeriodModel) -> AcademicPeriod:
        # Simple mapper or reused mapper
        # Assuming simple mapping for now
        from app.domain.value_objects.planning import PeriodCode
        return AcademicPeriod(
            id=model.id,
            code=PeriodCode(model.code),
            name=model.name,
            start_date=model.start_date,
            end_date=model.end_date,
            is_active=model.is_active
        )
