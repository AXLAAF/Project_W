"""API router for Reservations."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database import get_db
from app.dependencies import get_current_active_user
from app.core.models import User
from app.reservations.models import ReservationStatus
from app.reservations.schemas import (
    ReservationCreate,
    ReservationUpdate,
    ReservationReject,
    ReservationRead,
    ReservationWithResource,
    ReservationCalendarItem,
)
from app.reservations.services import ReservationService

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.post("", response_model=ReservationRead, status_code=201)
async def create_reservation(
    data: ReservationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new reservation."""
    service = ReservationService(db)
    return await service.create_reservation(current_user.id, data)


@router.get("/my-reservations", response_model=List[ReservationWithResource])
async def get_my_reservations(
    status: Optional[ReservationStatus] = Query(None),
    upcoming_only: bool = Query(False),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's reservations."""
    service = ReservationService(db)
    return await service.get_my_reservations(
        user_id=current_user.id,
        status=status,
        upcoming_only=upcoming_only,
        offset=offset,
        limit=limit,
    )


@router.get("/calendar/{resource_id}", response_model=List[ReservationCalendarItem])
async def get_resource_calendar(
    resource_id: int,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Get reservations for a resource (calendar view)."""
    service = ReservationService(db)
    return await service.get_resource_calendar(
        resource_id=resource_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/{reservation_id}", response_model=ReservationWithResource)
async def get_reservation(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a reservation by ID."""
    service = ReservationService(db)
    return await service.get_reservation(reservation_id)


@router.put("/{reservation_id}", response_model=ReservationRead)
async def update_reservation(
    reservation_id: int,
    data: ReservationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a reservation."""
    service = ReservationService(db)
    return await service.update_reservation(reservation_id, current_user.id, data)


@router.delete("/{reservation_id}", status_code=204)
async def cancel_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a reservation."""
    service = ReservationService(db)
    await service.cancel_reservation(reservation_id, current_user.id)


@router.post("/{reservation_id}/approve", response_model=ReservationRead)
async def approve_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve a pending reservation (admin only)."""
    # TODO: Add admin role check
    service = ReservationService(db)
    return await service.approve_reservation(reservation_id, current_user.id)


@router.post("/{reservation_id}/reject", response_model=ReservationRead)
async def reject_reservation(
    reservation_id: int,
    data: ReservationReject,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Reject a pending reservation (admin only)."""
    # TODO: Add admin role check
    service = ReservationService(db)
    return await service.reject_reservation(
        reservation_id, current_user.id, data.rejection_reason
    )


@router.post("/{reservation_id}/check-in", response_model=ReservationRead)
async def check_in(
    reservation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Check in to a reservation."""
    service = ReservationService(db)
    return await service.check_in(reservation_id, current_user.id)


@router.post("/{reservation_id}/check-out", response_model=ReservationRead)
async def check_out(
    reservation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Check out of a reservation."""
    service = ReservationService(db)
    return await service.check_out(reservation_id, current_user.id)
