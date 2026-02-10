"""
Create Reservation Use Case.
"""
from datetime import datetime
from typing import Optional

from app.domain.repositories.reservations_repository import IReservationRepository, IResourceRepository, IRuleRepository
from app.domain.entities.reservations.reservation import Reservation
from app.domain.services.availability_service import AvailabilityService
from app.domain.value_objects.reservations import ReservationStatus

class CreateReservationUseCase:
    def __init__(
        self,
        reservation_repo: IReservationRepository,
        resource_repo: IResourceRepository,
        rule_repo: IRuleRepository
    ):
        self.reservation_repo = reservation_repo
        self.resource_repo = resource_repo
        self.availability_service = AvailabilityService(reservation_repo, rule_repo)

    async def execute(
        self,
        resource_id: int,
        user_id: int,
        start_time: datetime,
        end_time: datetime,
        title: str,
        description: Optional[str] = None,
        attendees_count: Optional[int] = None
    ) -> Reservation:
        # 1. Get Resource
        resource = await self.resource_repo.get_by_id(resource_id)
        if not resource:
            raise ValueError(f"Resource with ID {resource_id} not found")

        # 2. Check Availability
        is_available = await self.availability_service.check_availability(
            resource=resource,
            start_time=start_time,
            end_time=end_time
        )
        if not is_available:
            raise ValueError("Resource is not available for the selected time slot")

        # 3. Create Reservation Entity
        reservation = Reservation(
            resource_id=resource_id,
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
            title=title,
            description=description,
            attendees_count=attendees_count,
            status=ReservationStatus.PENDING if resource.requires_approval else ReservationStatus.APPROVED
        )

        # 4. Save
        return await self.reservation_repo.save(reservation)
