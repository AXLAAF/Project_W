"""
Positions API router.
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User
from app.dependencies import get_current_active_user
from app.shared.database import get_db
from app.internships.models.internship_position import PositionModality
from app.internships.services.position_service import PositionService, PositionError
from app.internships.schemas.position import (
    PositionCreate,
    PositionUpdate,
    PositionRead,
    PositionWithCompany,
)

router = APIRouter(prefix="/internships/positions", tags=["positions"])


@router.get("", response_model=list[PositionWithCompany])
async def list_positions(
    db: Annotated[AsyncSession, Depends(get_db)],
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    company_id: Optional[int] = Query(None),
    modality: Optional[PositionModality] = Query(None),
    search: Optional[str] = Query(None, max_length=100),
    only_available: bool = Query(False),
) -> list[PositionWithCompany]:
    """
    List all internship positions with pagination and filters.
    """
    service = PositionService(db)
    positions, _ = await service.get_all(
        offset=offset,
        limit=limit,
        company_id=company_id,
        modality=modality,
        search=search,
        only_available=only_available,
    )
    return [PositionWithCompany.model_validate(p) for p in positions]


@router.get("/{position_id}", response_model=PositionWithCompany)
async def get_position(
    position_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PositionWithCompany:
    """
    Get position details by ID.
    """
    service = PositionService(db)
    position = await service.get_by_id(position_id)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found",
        )
    return PositionWithCompany.model_validate(position)


@router.post("", response_model=PositionRead, status_code=status.HTTP_201_CREATED)
async def create_position(
    data: PositionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> PositionRead:
    """
    Create a new internship position.
    """
    service = PositionService(db)
    try:
        position = await service.create(data)
        await db.commit()
        return PositionRead.model_validate(position)
    except PositionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{position_id}", response_model=PositionRead)
async def update_position(
    position_id: int,
    data: PositionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> PositionRead:
    """
    Update position information.
    """
    service = PositionService(db)
    try:
        position = await service.update(position_id, data)
        await db.commit()
        return PositionRead.model_validate(position)
    except PositionError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_position(
    position_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> None:
    """
    Deactivate a position (soft delete).
    """
    service = PositionService(db)
    try:
        await service.deactivate(position_id)
        await db.commit()
    except PositionError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
