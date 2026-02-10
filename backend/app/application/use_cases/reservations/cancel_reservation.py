"""
Cancel Reservation Use Case.
"""
from typing import Optional

from app.domain.repositories.reservations_repository import IReservationRepository
from app.domain.entities.reservations.reservation import Reservation
from app.domain.value_objects.reservations import ReservationStatus

class CancelReservationUseCase:
    def __init__(self, reservation_repo: IReservationRepository):
        self.reservation_repo = reservation_repo

    async def execute(self, reservation_id: int, user_id: int) -> Reservation:
        # 1. Get Reservation
        reservation = await self.reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise ValueError(f"Reservation with ID {reservation_id} not found")

        # 2. Check Permissions (Basic ownership check)
        # TODO: Add role-based check (e.g. Admin can cancel any) if needed via a PermissionService
        if reservation.user_id != user_id:
            raise ValueError("You do not have permission to cancel this reservation")

        # 3. Check Status
        if reservation.status in [ReservationStatus.CANCELLED, ReservationStatus.REJECTED, ReservationStatus.COMPLETED]:
            raise ValueError("Reservation cannot be cancelled in its current state")

        # 4. Cancel
        reservation.cancel()

        # 5. Save
        return await self.reservation_repo.update(reservation)
