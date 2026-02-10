"""
Reservations repository interface (Port).
"""
from abc import ABC, abstractmethod
from typing import Optional, Sequence, List
from datetime import datetime

from app.domain.entities.reservations.resource import Resource
from app.domain.entities.reservations.reservation import Reservation
from app.domain.entities.reservations.rule import ReservationRule
from app.domain.value_objects.reservations import ResourceType, ReservationStatus

class IResourceRepository(ABC):
    @abstractmethod
    async def get_by_id(self, resource_id: int) -> Optional[Resource]:
        pass

    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[Resource]:
        pass

    @abstractmethod
    async def save(self, resource: Resource) -> Resource:
        pass

    @abstractmethod
    async def update(self, resource: Resource) -> Resource:
        pass

    @abstractmethod
    async def list_resources(
        self,
        resource_type: Optional[ResourceType] = None,
        is_active: Optional[bool] = None,
        capacity_min: Optional[int] = None
    ) -> Sequence[Resource]:
        pass

class IReservationRepository(ABC):
    @abstractmethod
    async def get_by_id(self, reservation_id: int) -> Optional[Reservation]:
        pass

    @abstractmethod
    async def save(self, reservation: Reservation) -> Reservation:
        pass

    @abstractmethod
    async def update(self, reservation: Reservation) -> Reservation:
        pass

    @abstractmethod
    async def get_overlapping_reservations(
        self,
        resource_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_reservation_id: Optional[int] = None
    ) -> Sequence[Reservation]:
        pass

    @abstractmethod
    async def list_by_user(
        self,
        user_id: int,
        status: Optional[ReservationStatus] = None,
        start_date: Optional[datetime] = None
    ) -> Sequence[Reservation]:
        pass

    @abstractmethod
    async def list_by_resource(
        self,
        resource_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Sequence[Reservation]:
        pass

class IRuleRepository(ABC):
    @abstractmethod
    async def get_by_id(self, rule_id: int) -> Optional[ReservationRule]:
        pass

    @abstractmethod
    async def save(self, rule: ReservationRule) -> ReservationRule:
        pass
    
    @abstractmethod
    async def list_active_rules(self, resource_id: Optional[int] = None) -> Sequence[ReservationRule]:
        pass
