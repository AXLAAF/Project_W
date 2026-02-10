"""Repository for Resource operations."""
from typing import List, Optional

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.reservations.models import Resource, ResourceType, ResourceStatus
from app.reservations.schemas import ResourceCreate, ResourceUpdate


class ResourceRepository:
    """Repository for Resource CRUD operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: ResourceCreate) -> Resource:
        """Create a new resource."""
        resource = Resource(**data.model_dump())
        self.db.add(resource)
        await self.db.flush()
        await self.db.refresh(resource)
        return resource

    async def get_by_id(self, resource_id: int) -> Optional[Resource]:
        """Get a resource by ID."""
        result = await self.db.execute(
            select(Resource).where(Resource.id == resource_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Resource]:
        """Get a resource by code."""
        result = await self.db.execute(
            select(Resource).where(Resource.code == code)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        resource_type: Optional[ResourceType] = None,
        status: Optional[ResourceStatus] = None,
        building: Optional[str] = None,
        is_active: Optional[bool] = True,
        search: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> List[Resource]:
        """Get all resources with filters."""
        query = select(Resource)
        
        conditions = []
        if resource_type:
            conditions.append(Resource.resource_type == resource_type)
        if status:
            conditions.append(Resource.status == status)
        if building:
            conditions.append(Resource.building == building)
        if is_active is not None:
            conditions.append(Resource.is_active == is_active)
        if search:
            search_pattern = f"%{search}%"
            conditions.append(
                or_(
                    Resource.name.ilike(search_pattern),
                    Resource.code.ilike(search_pattern),
                    Resource.description.ilike(search_pattern),
                )
            )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(Resource.name).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, resource_id: int, data: ResourceUpdate) -> Optional[Resource]:
        """Update a resource."""
        resource = await self.get_by_id(resource_id)
        if not resource:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(resource, field, value)
        
        await self.db.flush()
        await self.db.refresh(resource)
        return resource

    async def delete(self, resource_id: int) -> bool:
        """Delete a resource."""
        resource = await self.get_by_id(resource_id)
        if not resource:
            return False
        
        await self.db.delete(resource)
        await self.db.flush()
        return True

    async def get_buildings(self) -> List[str]:
        """Get list of unique buildings."""
        result = await self.db.execute(
            select(Resource.building)
            .where(Resource.building.isnot(None))
            .distinct()
            .order_by(Resource.building)
        )
        return [row[0] for row in result.all()]

    async def set_status(self, resource_id: int, status: ResourceStatus) -> Optional[Resource]:
        """Update resource status."""
        resource = await self.get_by_id(resource_id)
        if not resource:
            return None
        
        resource.status = status
        await self.db.flush()
        await self.db.refresh(resource)
        return resource
