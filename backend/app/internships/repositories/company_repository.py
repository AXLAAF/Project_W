"""
Company repository for database operations.
"""
from typing import Optional, Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.internships.models.company import Company


class CompanyRepository:
    """Repository for Company database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, company_id: int) -> Optional[Company]:
        """Get company by ID with positions."""
        query = (
            select(Company)
            .options(selectinload(Company.positions))
            .where(Company.id == company_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_rfc(self, rfc: str) -> Optional[Company]:
        """Get company by RFC."""
        query = select(Company).where(Company.rfc == rfc)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        is_verified: Optional[bool] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> tuple[Sequence[Company], int]:
        """Get all companies with pagination and filters."""
        query = select(Company)
        count_query = select(func.count()).select_from(Company)

        if is_verified is not None:
            query = query.where(Company.is_verified == is_verified)
            count_query = count_query.where(Company.is_verified == is_verified)

        if is_active is not None:
            query = query.where(Company.is_active == is_active)
            count_query = count_query.where(Company.is_active == is_active)

        if search:
            search_pattern = f"%{search}%"
            query = query.where(Company.name.ilike(search_pattern))
            count_query = count_query.where(Company.name.ilike(search_pattern))

        query = query.offset(offset).limit(limit).order_by(Company.name)

        result = await self.session.execute(query)
        count_result = await self.session.execute(count_query)

        return result.scalars().all(), count_result.scalar_one()

    async def create(self, **kwargs) -> Company:
        """Create a new company."""
        company = Company(**kwargs)
        self.session.add(company)
        await self.session.flush()
        return company

    async def update(self, company: Company, **kwargs) -> Company:
        """Update company fields."""
        for key, value in kwargs.items():
            if hasattr(company, key) and value is not None:
                setattr(company, key, value)
        await self.session.flush()
        return company

    async def delete(self, company: Company) -> None:
        """Delete a company."""
        await self.session.delete(company)

    async def verify(self, company: Company, is_verified: bool = True) -> Company:
        """Verify or unverify a company."""
        company.is_verified = is_verified
        await self.session.flush()
        return company
