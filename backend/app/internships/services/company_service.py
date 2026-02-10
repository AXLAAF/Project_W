"""
Company service for business logic.
"""
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.internships.models.company import Company
from app.internships.repositories.company_repository import CompanyRepository
from app.internships.schemas.company import CompanyCreate, CompanyUpdate


class CompanyError(Exception):
    """Raised when company operation fails."""
    pass


class CompanyService:
    """Service for company business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CompanyRepository(session)

    async def get_by_id(self, company_id: int) -> Optional[Company]:
        """Get company by ID."""
        return await self.repo.get_by_id(company_id)

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        is_verified: Optional[bool] = None,
        is_active: Optional[bool] = True,
        search: Optional[str] = None,
    ) -> tuple[Sequence[Company], int]:
        """Get all companies with filters."""
        return await self.repo.get_all(
            offset=offset,
            limit=limit,
            is_verified=is_verified,
            is_active=is_active,
            search=search,
        )

    async def create(self, data: CompanyCreate) -> Company:
        """Create a new company."""
        # Check if RFC already exists
        existing = await self.repo.get_by_rfc(data.rfc)
        if existing:
            raise CompanyError("A company with this RFC already exists")

        return await self.repo.create(**data.model_dump())

    async def update(self, company_id: int, data: CompanyUpdate) -> Company:
        """Update a company."""
        company = await self.repo.get_by_id(company_id)
        if not company:
            raise CompanyError("Company not found")

        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(company, **update_data)

    async def verify(self, company_id: int, is_verified: bool = True) -> Company:
        """Verify or unverify a company (admin only)."""
        company = await self.repo.get_by_id(company_id)
        if not company:
            raise CompanyError("Company not found")

        return await self.repo.verify(company, is_verified)

    async def deactivate(self, company_id: int) -> Company:
        """Deactivate a company."""
        company = await self.repo.get_by_id(company_id)
        if not company:
            raise CompanyError("Company not found")

        return await self.repo.update(company, is_active=False)
