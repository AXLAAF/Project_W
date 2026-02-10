"""
SQLAlchemy implementations of Reservations repositories.
"""
from typing import Optional, Sequence, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.domain.repositories.reservations_repository import IResourceRepository, IReservationRepository, IRuleRepository
from app.domain.entities.reservations.resource import Resource
from app.domain.entities.reservations.reservation import Reservation
from app.domain.entities.reservations.rule import ReservationRule
from app.domain.value_objects.reservations import ResourceType, ReservationStatus
from app.infrastructure.persistence.sqlalchemy.reservation_mappers import ResourceMapper, ReservationMapper, RuleMapper
from app.reservations.models.resource import Resource as ResourceModel
from app.reservations.models.reservation import Reservation as ReservationModel
from app.reservations.models.reservation_rule import ReservationRule as RuleModel

class SQLAlchemyResourceRepository(IResourceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, resource_id: int) -> Optional[Resource]:
        result = await self.session.execute(select(ResourceModel).where(ResourceModel.id == resource_id))
        model = result.scalar_one_or_none()
        return ResourceMapper.to_entity(model) if model else None

    async def get_by_code(self, code: str) -> Optional[Resource]:
        result = await self.session.execute(select(ResourceModel).where(ResourceModel.code == code))
        model = result.scalar_one_or_none()
        return ResourceMapper.to_entity(model) if model else None

    async def save(self, resource: Resource) -> Resource:
        model = ResourceMapper.to_model(resource)
        if resource.id:
            await self.session.merge(model)
        else:
            self.session.add(model)
        await self.session.flush()
        return ResourceMapper.to_entity(model)

    async def update(self, resource: Resource) -> Resource:
        return await self.save(resource)

    async def list_resources(
        self,
        resource_type: Optional[ResourceType] = None,
        is_active: Optional[bool] = None,
        capacity_min: Optional[int] = None
    ) -> Sequence[Resource]:
        query = select(ResourceModel)
        if resource_type:
            query = query.where(ResourceModel.resource_type == resource_type.value)
        if is_active is not None:
            query = query.where(ResourceModel.is_active == is_active)
        if capacity_min is not None:
            query = query.where(ResourceModel.capacity >= capacity_min)
            
        result = await self.session.execute(query)
        return [ResourceMapper.to_entity(m) for m in result.scalars().all()]

class SQLAlchemyReservationRepository(IReservationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, reservation_id: int) -> Optional[Reservation]:
        result = await self.session.execute(select(ReservationModel).where(ReservationModel.id == reservation_id))
        model = result.scalar_one_or_none()
        return ReservationMapper.to_entity(model) if model else None

    async def save(self, reservation: Reservation) -> Reservation:
        model = ReservationMapper.to_model(reservation)
        if reservation.id:
            # For updates, we need to be careful not to overwrite None fields if not intended,
            # but standard save often assumes full object replacement or merge.
            await self.session.merge(model)
        else:
            self.session.add(model)
        await self.session.flush()
        return ReservationMapper.to_entity(model)

    async def update(self, reservation: Reservation) -> Reservation:
        return await self.save(reservation)

    async def get_overlapping_reservations(
        self,
        resource_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_reservation_id: Optional[int] = None
    ) -> Sequence[Reservation]:
        query = select(ReservationModel).where(
            ReservationModel.resource_id == resource_id,
            ReservationModel.status.not_in(["CANCELLED", "REJECTED"]),
            or_(
                and_(ReservationModel.start_time < end_time, ReservationModel.end_time > start_time)
            )
        )
        if exclude_reservation_id:
            query = query.where(ReservationModel.id != exclude_reservation_id)
            
        result = await self.session.execute(query)
        return [ReservationMapper.to_entity(m) for m in result.scalars().all()]

    async def list_by_user(
        self,
        user_id: int,
        status: Optional[ReservationStatus] = None,
        start_date: Optional[datetime] = None
    ) -> Sequence[Reservation]:
        query = select(ReservationModel).where(ReservationModel.user_id == user_id)
        if status:
            query = query.where(ReservationModel.status == status.value)
        if start_date:
            query = query.where(ReservationModel.start_time >= start_date)
            
        result = await self.session.execute(query)
        return [ReservationMapper.to_entity(m) for m in result.scalars().all()]

    async def list_by_resource(
        self,
        resource_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Sequence[Reservation]:
        query = select(ReservationModel).where(
            ReservationModel.resource_id == resource_id,
            ReservationModel.start_time >= start_date,
            ReservationModel.end_time <= end_date
        )
        result = await self.session.execute(query)
        return [ReservationMapper.to_entity(m) for m in result.scalars().all()]

class SQLAlchemyRuleRepository(IRuleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, rule_id: int) -> Optional[ReservationRule]:
        result = await self.session.execute(select(RuleModel).where(RuleModel.id == rule_id))
        model = result.scalar_one_or_none()
        return RuleMapper.to_entity(model) if model else None

    async def save(self, rule: ReservationRule) -> ReservationRule:
        model = RuleMapper.to_model(rule)
        if rule.id:
            await self.session.merge(model)
        else:
            self.session.add(model)
        await self.session.flush()
        return RuleMapper.to_entity(model)

    async def list_active_rules(self, resource_id: Optional[int] = None) -> Sequence[ReservationRule]:
        query = select(RuleModel).where(RuleModel.is_active == True)
        # Get global rules (resource_id is None) AND specific resource rules
        if resource_id:
            query = query.where(or_(RuleModel.resource_id == None, RuleModel.resource_id == resource_id))
        else:
            query = query.where(RuleModel.resource_id == None)
            
        result = await self.session.execute(query)
        return [RuleMapper.to_entity(m) for m in result.scalars().all()]
