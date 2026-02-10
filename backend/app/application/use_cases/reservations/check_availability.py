"""
Check Availability Use Case.
"""
from datetime import datetime

from app.domain.repositories.reservations_repository import IResourceRepository, IReservationRepository, IRuleRepository
from app.domain.services.availability_service import AvailabilityService

class CheckAvailabilityUseCase:
    def __init__(
        self,
        resource_repo: IResourceRepository,
        reservation_repo: IReservationRepository,
        rule_repo: IRuleRepository
    ):
        self.resource_repo = resource_repo
        self.availability_service = AvailabilityService(reservation_repo, rule_repo)

    async def execute(
        self,
        resource_id: int,
        start_time: datetime,
        end_time: datetime
    ) -> bool:
        # 1. Get Resource
        resource = await self.resource_repo.get_by_id(resource_id)
        if not resource:
            raise ValueError(f"Resource with ID {resource_id} not found")

        # 2. Check
        return await self.availability_service.check_availability(
            resource=resource,
            start_time=start_time,
            end_time=end_time
        )
