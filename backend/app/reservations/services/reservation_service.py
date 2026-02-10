"""Service for Reservation operations with conflict validation."""
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.reservations.models import Reservation, ReservationStatus
from app.reservations.schemas import ReservationCreate, ReservationUpdate
from app.reservations.repositories import (
    ResourceRepository,
    ReservationRepository,
    RuleRepository,
    SanctionRepository,
)


class ReservationService:
    """Business logic for Reservation operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.reservation_repo = ReservationRepository(db)
        self.resource_repo = ResourceRepository(db)
        self.rule_repo = RuleRepository(db)
        self.sanction_repo = SanctionRepository(db)

    async def create_reservation(self, user_id: int, data: ReservationCreate) -> Reservation:
        """Create a new reservation with conflict checking."""
        # Check user sanctions
        if await self.sanction_repo.user_has_active_sanction(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create reservation: user has an active sanction",
            )
        
        # Get resource and validate
        resource = await self.resource_repo.get_by_id(data.resource_id)
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found",
            )
        
        if not resource.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resource is not available for reservations",
            )
        
        # Validate time constraints
        now = datetime.now(data.start_time.tzinfo)
        if data.start_time <= now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reservation start time must be in the future",
            )
        
        # Check advance booking limit
        max_advance = timedelta(days=resource.advance_booking_days)
        if data.start_time > now + max_advance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot book more than {resource.advance_booking_days} days in advance",
            )
        
        # Calculate duration and validate
        duration_minutes = int((data.end_time - data.start_time).total_seconds() / 60)
        
        if duration_minutes < resource.min_reservation_minutes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Minimum reservation duration is {resource.min_reservation_minutes} minutes",
            )
        
        if duration_minutes > resource.max_reservation_minutes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum reservation duration is {resource.max_reservation_minutes} minutes",
            )
        
        # Check for conflicts
        conflicts = await self.reservation_repo.check_conflicts(
            resource_id=data.resource_id,
            start_time=data.start_time,
            end_time=data.end_time,
        )
        
        if conflicts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Time slot conflicts with existing reservation(s)",
            )
        
        # Create reservation (auto-approve if resource doesn't require approval)
        return await self.reservation_repo.create(
            user_id=user_id,
            data=data,
            auto_approve=not resource.requires_approval,
        )

    async def get_reservation(self, reservation_id: int) -> Reservation:
        """Get a reservation by ID."""
        reservation = await self.reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found",
            )
        return reservation

    async def get_my_reservations(
        self,
        user_id: int,
        status: Optional[ReservationStatus] = None,
        upcoming_only: bool = False,
        offset: int = 0,
        limit: int = 50,
    ) -> List[Reservation]:
        """Get user's reservations."""
        return await self.reservation_repo.get_user_reservations(
            user_id=user_id,
            status=status,
            upcoming_only=upcoming_only,
            offset=offset,
            limit=limit,
        )

    async def get_resource_calendar(
        self,
        resource_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Reservation]:
        """Get reservations for a resource in a date range (calendar view)."""
        # Validate resource exists
        resource = await self.resource_repo.get_by_id(resource_id)
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found",
            )
        
        return await self.reservation_repo.get_resource_reservations(
            resource_id=resource_id,
            start_date=start_date,
            end_date=end_date,
        )

    async def update_reservation(
        self,
        reservation_id: int,
        user_id: int,
        data: ReservationUpdate,
    ) -> Reservation:
        """Update a reservation."""
        reservation = await self.get_reservation(reservation_id)
        
        # Only owner can update
        if reservation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this reservation",
            )
        
        # Can only update pending reservations
        if reservation.status not in [ReservationStatus.PENDING, ReservationStatus.APPROVED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot update reservation with status {reservation.status}",
            )
        
        # If updating time, check for conflicts
        if data.start_time or data.end_time:
            start = data.start_time or reservation.start_time
            end = data.end_time or reservation.end_time
            
            conflicts = await self.reservation_repo.check_conflicts(
                resource_id=reservation.resource_id,
                start_time=start,
                end_time=end,
                exclude_reservation_id=reservation_id,
            )
            
            if conflicts:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Updated time slot conflicts with existing reservation(s)",
                )
        
        return await self.reservation_repo.update(reservation_id, data)

    async def cancel_reservation(self, reservation_id: int, user_id: int) -> Reservation:
        """Cancel a reservation."""
        reservation = await self.get_reservation(reservation_id)
        
        # Only owner can cancel
        if reservation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this reservation",
            )
        
        if reservation.status in [ReservationStatus.CANCELLED, ReservationStatus.COMPLETED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel reservation with status {reservation.status}",
            )
        
        return await self.reservation_repo.cancel(reservation_id)

    async def approve_reservation(
        self,
        reservation_id: int,
        admin_user_id: int,
    ) -> Reservation:
        """Approve a pending reservation."""
        reservation = await self.get_reservation(reservation_id)
        
        if reservation.status != ReservationStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending reservations can be approved",
            )
        
        return await self.reservation_repo.approve(reservation_id, admin_user_id)

    async def reject_reservation(
        self,
        reservation_id: int,
        admin_user_id: int,
        reason: str,
    ) -> Reservation:
        """Reject a pending reservation."""
        reservation = await self.get_reservation(reservation_id)
        
        if reservation.status != ReservationStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending reservations can be rejected",
            )
        
        return await self.reservation_repo.reject(reservation_id, admin_user_id, reason)

    async def check_in(self, reservation_id: int, user_id: int) -> Reservation:
        """Check in to a reservation."""
        reservation = await self.get_reservation(reservation_id)
        
        if reservation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to check in to this reservation",
            )
        
        if reservation.status != ReservationStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only check in to approved reservations",
            )
        
        return await self.reservation_repo.check_in(reservation_id)

    async def check_out(self, reservation_id: int, user_id: int) -> Reservation:
        """Check out of a reservation."""
        reservation = await self.get_reservation(reservation_id)
        
        if reservation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to check out of this reservation",
            )
        
        if not reservation.checked_in_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must check in before checking out",
            )
        
        return await self.reservation_repo.check_out(reservation_id)
