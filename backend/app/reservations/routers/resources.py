"""API router for Resources."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database import get_db
from app.reservations.models import ResourceType, ResourceStatus
from app.reservations.schemas import (
    ResourceCreate,
    ResourceUpdate,
    ResourceRead,
    ResourceList,
)
from app.reservations.services import ResourceService

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.post("", response_model=ResourceRead, status_code=201)
async def create_resource(
    data: ResourceCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new resource."""
    service = ResourceService(db)
    return await service.create_resource(data)


@router.get("", response_model=List[ResourceList])
async def list_resources(
    resource_type: Optional[ResourceType] = Query(None),
    status: Optional[ResourceStatus] = Query(None),
    building: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(True),
    search: Optional[str] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List resources with optional filters."""
    service = ResourceService(db)
    return await service.list_resources(
        resource_type=resource_type,
        status=status,
        building=building,
        is_active=is_active,
        search=search,
        offset=offset,
        limit=limit,
    )


@router.get("/buildings", response_model=List[str])
async def get_buildings(db: AsyncSession = Depends(get_db)):
    """Get list of unique buildings."""
    service = ResourceService(db)
    return await service.get_buildings()


@router.get("/{resource_id}", response_model=ResourceRead)
async def get_resource(
    resource_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a resource by ID."""
    service = ResourceService(db)
    return await service.get_resource(resource_id)


@router.put("/{resource_id}", response_model=ResourceRead)
async def update_resource(
    resource_id: int,
    data: ResourceUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a resource."""
    service = ResourceService(db)
    return await service.update_resource(resource_id, data)


@router.delete("/{resource_id}", status_code=204)
async def delete_resource(
    resource_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a resource."""
    service = ResourceService(db)
    await service.delete_resource(resource_id)


@router.put("/{resource_id}/status", response_model=ResourceRead)
async def set_resource_status(
    resource_id: int,
    status: ResourceStatus,
    db: AsyncSession = Depends(get_db),
):
    """Update resource status."""
    service = ResourceService(db)
    return await service.set_status(resource_id, status)
