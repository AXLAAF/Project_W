"""
Position service for business logic.
"""
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.internships.models.internship_position import InternshipPosition, PositionModality
from app.internships.repositories.position_repository import PositionRepository
from app.internships.repositories.company_repository import CompanyRepository
from app.internships.schemas.position import PositionCreate, PositionUpdate


class PositionError(Exception):
    """Raised when position operation fails."""
    pass


class PositionService:
    """Service for position business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PositionRepository(session)
        self.company_repo = CompanyRepository(session)

    async def get_by_id(self, position_id: int) -> Optional[InternshipPosition]:
        """Get position by ID."""
        return await self.repo.get_by_id(position_id)

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        company_id: Optional[int] = None,
        modality: Optional[PositionModality] = None,
        is_active: Optional[bool] = True,
        search: Optional[str] = None,
        only_available: bool = False,
    ) -> tuple[Sequence[InternshipPosition], int]:
        """Get all positions with filters."""
        return await self.repo.get_all(
            offset=offset,
            limit=limit,
            company_id=company_id,
            modality=modality,
            is_active=is_active,
            search=search,
            only_available=only_available,
        )

    async def create(self, data: PositionCreate) -> InternshipPosition:
        """Create a new position."""
        # Verify company exists and is verified
        company = await self.company_repo.get_by_id(data.company_id)
        if not company:
            raise PositionError("Company not found")
        if not company.is_verified:
            raise PositionError("Company must be verified to create positions")
        if not company.is_active:
            raise PositionError("Company is not active")

        return await self.repo.create(**data.model_dump())

    async def update(self, position_id: int, data: PositionUpdate) -> InternshipPosition:
        """Update a position."""
        position = await self.repo.get_by_id(position_id)
        if not position:
            raise PositionError("Position not found")

        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(position, **update_data)

    async def deactivate(self, position_id: int) -> InternshipPosition:
        """Deactivate a position."""
        position = await self.repo.get_by_id(position_id)
        if not position:
            raise PositionError("Position not found")

        return await self.repo.update(position, is_active=False)

    async def get_by_company(self, company_id: int) -> Sequence[InternshipPosition]:
        """Get all positions for a company."""
        return await self.repo.get_by_company(company_id)
