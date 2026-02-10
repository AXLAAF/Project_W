"""Service for Resource operations."""
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.reservations.models import Resource, ResourceType, ResourceStatus
from app.reservations.schemas import ResourceCreate, ResourceUpdate
from app.reservations.repositories import ResourceRepository


class ResourceService:
    """Business logic for Resource operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ResourceRepository(db)

    async def create_resource(self, data: ResourceCreate) -> Resource:
        """Create a new resource."""
        # Check for duplicate code
        existing = await self.repository.get_by_code(data.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Resource with code '{data.code}' already exists",
            )
        
        return await self.repository.create(data)

    async def get_resource(self, resource_id: int) -> Resource:
        """Get a resource by ID."""
        resource = await self.repository.get_by_id(resource_id)
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found",
            )
        return resource

    async def list_resources(
        self,
        resource_type: Optional[ResourceType] = None,
        status: Optional[ResourceStatus] = None,
        building: Optional[str] = None,
        is_active: Optional[bool] = True,
        search: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> List[Resource]:
        """List resources with filters."""
        return await self.repository.get_all(
            resource_type=resource_type,
            status=status,
            building=building,
            is_active=is_active,
            search=search,
            offset=offset,
            limit=limit,
        )

    async def update_resource(self, resource_id: int, data: ResourceUpdate) -> Resource:
        """Update a resource."""
        resource = await self.repository.update(resource_id, data)
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found",
            )
        return resource

    async def delete_resource(self, resource_id: int) -> None:
        """Delete a resource."""
        deleted = await self.repository.delete(resource_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found",
            )

    async def set_status(self, resource_id: int, status: ResourceStatus) -> Resource:
        """Update resource status."""
        resource = await self.repository.set_status(resource_id, status)
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found",
            )
        return resource

    async def get_buildings(self) -> List[str]:
        """Get list of unique buildings."""
        return await self.repository.get_buildings()
