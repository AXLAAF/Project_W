"""Repository for Reservation operations."""
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.reservations.models import Reservation, ReservationStatus
from app.reservations.schemas import ReservationCreate, ReservationUpdate


class ReservationRepository:
    """Repository for Reservation CRUD operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: int, data: ReservationCreate, auto_approve: bool = False) -> Reservation:
        """Create a new reservation."""
        status = ReservationStatus.APPROVED if auto_approve else ReservationStatus.PENDING
        reservation = Reservation(
            user_id=user_id,
            status=status,
            **data.model_dump()
        )
        self.db.add(reservation)
        await self.db.flush()
        await self.db.refresh(reservation)
        return reservation

    async def get_by_id(self, reservation_id: int) -> Optional[Reservation]:
        """Get a reservation by ID."""
        result = await self.db.execute(
            select(Reservation)
            .options(selectinload(Reservation.resource))
            .where(Reservation.id == reservation_id)
        )
        return result.scalar_one_or_none()

    async def get_user_reservations(
        self,
        user_id: int,
        status: Optional[ReservationStatus] = None,
        upcoming_only: bool = False,
        offset: int = 0,
        limit: int = 50,
    ) -> List[Reservation]:
        """Get reservations for a user."""
        query = select(Reservation).options(selectinload(Reservation.resource))
        
        conditions = [Reservation.user_id == user_id]
        if status:
            conditions.append(Reservation.status == status)
        if upcoming_only:
            conditions.append(Reservation.start_time >= datetime.now())
        
        query = query.where(and_(*conditions))
        query = query.order_by(Reservation.start_time.desc()).offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_resource_reservations(
        self,
        resource_id: int,
        start_date: datetime,
        end_date: datetime,
        status: Optional[List[ReservationStatus]] = None,
    ) -> List[Reservation]:
        """Get reservations for a resource in a date range."""
        query = select(Reservation).where(
            and_(
                Reservation.resource_id == resource_id,
                Reservation.start_time < end_date,
                Reservation.end_time > start_date,
            )
        )
        
        if status:
            query = query.where(Reservation.status.in_(status))
        else:
            # By default, exclude cancelled reservations
            query = query.where(
                Reservation.status.not_in([ReservationStatus.CANCELLED, ReservationStatus.REJECTED])
            )
        
        query = query.order_by(Reservation.start_time)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def check_conflicts(
        self,
        resource_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_reservation_id: Optional[int] = None,
    ) -> List[Reservation]:
        """Check for conflicting reservations."""
        query = select(Reservation).where(
            and_(
                Reservation.resource_id == resource_id,
                Reservation.status.in_([
                    ReservationStatus.PENDING,
                    ReservationStatus.APPROVED,
                ]),
                # Check for overlap
                Reservation.start_time < end_time,
                Reservation.end_time > start_time,
            )
        )
        
        if exclude_reservation_id:
            query = query.where(Reservation.id != exclude_reservation_id)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, reservation_id: int, data: ReservationUpdate) -> Optional[Reservation]:
        """Update a reservation."""
        reservation = await self.get_by_id(reservation_id)
        if not reservation:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(reservation, field, value)
        
        await self.db.flush()
        await self.db.refresh(reservation)
        return reservation

    async def approve(self, reservation_id: int, approved_by_id: int) -> Optional[Reservation]:
        """Approve a reservation."""
        reservation = await self.get_by_id(reservation_id)
        if not reservation:
            return None
        
        reservation.status = ReservationStatus.APPROVED
        reservation.approved_by_id = approved_by_id
        reservation.approved_at = datetime.now()
        
        await self.db.flush()
        await self.db.refresh(reservation)
        return reservation

    async def reject(self, reservation_id: int, approved_by_id: int, reason: str) -> Optional[Reservation]:
        """Reject a reservation."""
        reservation = await self.get_by_id(reservation_id)
        if not reservation:
            return None
        
        reservation.status = ReservationStatus.REJECTED
        reservation.approved_by_id = approved_by_id
        reservation.approved_at = datetime.now()
        reservation.rejection_reason = reason
        
        await self.db.flush()
        await self.db.refresh(reservation)
        return reservation

    async def cancel(self, reservation_id: int) -> Optional[Reservation]:
        """Cancel a reservation."""
        reservation = await self.get_by_id(reservation_id)
        if not reservation:
            return None
        
        reservation.status = ReservationStatus.CANCELLED
        await self.db.flush()
        await self.db.refresh(reservation)
        return reservation

    async def check_in(self, reservation_id: int) -> Optional[Reservation]:
        """Check in to a reservation."""
        reservation = await self.get_by_id(reservation_id)
        if not reservation:
            return None
        
        reservation.checked_in_at = datetime.now()
        await self.db.flush()
        await self.db.refresh(reservation)
        return reservation

    async def check_out(self, reservation_id: int) -> Optional[Reservation]:
        """Check out of a reservation."""
        reservation = await self.get_by_id(reservation_id)
        if not reservation:
            return None
        
        reservation.checked_out_at = datetime.now()
        reservation.status = ReservationStatus.COMPLETED
        await self.db.flush()
        await self.db.refresh(reservation)
        return reservation

    async def mark_no_show(self, reservation_id: int) -> Optional[Reservation]:
        """Mark a reservation as no-show."""
        reservation = await self.get_by_id(reservation_id)
        if not reservation:
            return None
        
        reservation.status = ReservationStatus.NO_SHOW
        await self.db.flush()
        await self.db.refresh(reservation)
        return reservation
