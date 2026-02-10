"""
InternshipPosition repository for database operations.
"""
from typing import Optional, Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.internships.models.internship_position import InternshipPosition, PositionModality
from app.internships.models.company import Company


class PositionRepository:
    """Repository for InternshipPosition database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, position_id: int) -> Optional[InternshipPosition]:
        """Get position by ID with company."""
        query = (
            select(InternshipPosition)
            .options(selectinload(InternshipPosition.company))
            .where(InternshipPosition.id == position_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        company_id: Optional[int] = None,
        modality: Optional[PositionModality] = None,
        is_active: Optional[bool] = True,
        search: Optional[str] = None,
        min_gpa: Optional[float] = None,
        only_available: bool = False,
    ) -> tuple[Sequence[InternshipPosition], int]:
        """Get all positions with pagination and filters."""
        query = select(InternshipPosition).options(selectinload(InternshipPosition.company))
        count_query = select(func.count()).select_from(InternshipPosition)

        # Only show positions from verified companies
        query = query.join(Company).where(Company.is_verified == True)
        count_query = count_query.join(Company).where(Company.is_verified == True)

        if company_id is not None:
            query = query.where(InternshipPosition.company_id == company_id)
            count_query = count_query.where(InternshipPosition.company_id == company_id)

        if modality is not None:
            query = query.where(InternshipPosition.modality == modality)
            count_query = count_query.where(InternshipPosition.modality == modality)

        if is_active is not None:
            query = query.where(InternshipPosition.is_active == is_active)
            count_query = count_query.where(InternshipPosition.is_active == is_active)

        if search:
            search_pattern = f"%{search}%"
            query = query.where(InternshipPosition.title.ilike(search_pattern))
            count_query = count_query.where(InternshipPosition.title.ilike(search_pattern))

        if only_available:
            query = query.where(InternshipPosition.filled_count < InternshipPosition.capacity)
            count_query = count_query.where(InternshipPosition.filled_count < InternshipPosition.capacity)

        query = query.offset(offset).limit(limit).order_by(InternshipPosition.created_at.desc())

        result = await self.session.execute(query)
        count_result = await self.session.execute(count_query)

        return result.scalars().all(), count_result.scalar_one()

    async def get_by_company(self, company_id: int) -> Sequence[InternshipPosition]:
        """Get all positions for a company."""
        query = (
            select(InternshipPosition)
            .where(InternshipPosition.company_id == company_id)
            .order_by(InternshipPosition.created_at.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, **kwargs) -> InternshipPosition:
        """Create a new position."""
        position = InternshipPosition(**kwargs)
        self.session.add(position)
        await self.session.flush()
        return position

    async def update(self, position: InternshipPosition, **kwargs) -> InternshipPosition:
        """Update position fields."""
        for key, value in kwargs.items():
            if hasattr(position, key) and value is not None:
                setattr(position, key, value)
        await self.session.flush()
        return position

    async def delete(self, position: InternshipPosition) -> None:
        """Delete a position."""
        await self.session.delete(position)

    async def increment_filled_count(self, position: InternshipPosition) -> InternshipPosition:
        """Increment the filled count when an application is approved."""
        position.filled_count += 1
        await self.session.flush()
        return position

    async def decrement_filled_count(self, position: InternshipPosition) -> InternshipPosition:
        """Decrement the filled count when an internship is cancelled."""
        if position.filled_count > 0:
            position.filled_count -= 1
        await self.session.flush()
        return position
