"""
Availability service domain service.
"""
from typing import List, Optional
from datetime import datetime

from app.domain.entities.reservations.resource import Resource
from app.domain.entities.reservations.reservation import Reservation
from app.domain.entities.reservations.rule import ReservationRule
from app.domain.value_objects.reservations import TimeSlot, ResourceStatus
from app.domain.repositories.reservations_repository import IReservationRepository, IRuleRepository

class AvailabilityService:
    def __init__(self, reservation_repo: IReservationRepository, rule_repo: IRuleRepository):
        self.reservation_repo = reservation_repo
        self.rule_repo = rule_repo

    async def check_availability(
        self,
        resource: Resource,
        start_time: datetime,
        end_time: datetime,
        exclude_reservation_id: Optional[int] = None
    ) -> bool:
        """
        Check if a resource is available for a given time slot.
        Checks:
        1. Resource status
        2. Time slot validation
        3. Rules (operating hours, blocks) - TODO: Implement detailed rule checking
        4. Overlapping reservations
        """
        # 1. Resource status
        if not resource.is_available():
            return False

        # 2. Time slot
        try:
            slot = TimeSlot(start_time, end_time)
        except ValueError:
            return False

        # 3. Rules (Basic implementation for now)
        # TODO: Implement sophisticated rule checking against rule_repo

        # 4. Overlapping reservations
        overlapping = await self.reservation_repo.get_overlapping_reservations(
            resource_id=resource.id,
            start_time=start_time,
            end_time=end_time,
            exclude_reservation_id=exclude_reservation_id
        )
        
        return len(overlapping) == 0
