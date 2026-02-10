"""
SQLAlchemy mappers for Reservations module.
"""
from app.reservations.models.resource import Resource as ResourceModel, ResourceType as ResourceTypeModel, ResourceStatus as ResourceStatusModel
from app.reservations.models.reservation import Reservation as ReservationModel, ReservationStatus as ReservationStatusModel
from app.reservations.models.reservation_rule import ReservationRule as RuleModel, RuleType as RuleTypeModel
from app.domain.entities.reservations.resource import Resource
from app.domain.entities.reservations.reservation import Reservation
from app.domain.entities.reservations.rule import ReservationRule
from app.domain.value_objects.reservations import ResourceType, ResourceStatus, ReservationStatus, RuleType

class ResourceMapper:
    @staticmethod
    def to_entity(model: ResourceModel) -> Resource:
        return Resource(
            id=model.id,
            name=model.name,
            code=model.code,
            resource_type=ResourceType(model.resource_type.value),
            description=model.description,
            location=model.location,
            building=model.building,
            floor=model.floor,
            capacity=model.capacity,
            features=model.features,
            status=ResourceStatus(model.status.value),
            is_active=model.is_active,
            image_url=model.image_url,
            min_reservation_minutes=model.min_reservation_minutes,
            max_reservation_minutes=model.max_reservation_minutes,
            advance_booking_days=model.advance_booking_days,
            requires_approval=model.requires_approval,
            responsible_user_id=model.responsible_user_id,
            created_at=model.created_at
        )

    @staticmethod
    def to_model(entity: Resource) -> ResourceModel:
        return ResourceModel(
            id=entity.id,
            name=entity.name,
            code=entity.code,
            resource_type=ResourceTypeModel(entity.resource_type.value),
            description=entity.description,
            location=entity.location,
            building=entity.building,
            floor=entity.floor,
            capacity=entity.capacity,
            features=entity.features,
            status=ResourceStatusModel(entity.status.value),
            is_active=entity.is_active,
            image_url=entity.image_url,
            min_reservation_minutes=entity.min_reservation_minutes,
            max_reservation_minutes=entity.max_reservation_minutes,
            advance_booking_days=entity.advance_booking_days,
            requires_approval=entity.requires_approval,
            responsible_user_id=entity.responsible_user_id,
            # created_at handled by DB defaults if None
        )

class ReservationMapper:
    @staticmethod
    def to_entity(model: ReservationModel) -> Reservation:
        return Reservation(
            id=model.id,
            resource_id=model.resource_id,
            user_id=model.user_id,
            start_time=model.start_time,
            end_time=model.end_time,
            title=model.title,
            description=model.description,
            attendees_count=model.attendees_count,
            status=ReservationStatus(model.status.value),
            approved_by_id=model.approved_by_id,
            approved_at=model.approved_at,
            rejection_reason=model.rejection_reason,
            checked_in_at=model.checked_in_at,
            checked_out_at=model.checked_out_at,
            is_recurring=model.is_recurring,
            recurrence_pattern=model.recurrence_pattern,
            parent_reservation_id=model.parent_reservation_id,
            created_at=model.created_at
        )

    @staticmethod
    def to_model(entity: Reservation) -> ReservationModel:
        return ReservationModel(
            id=entity.id,
            resource_id=entity.resource_id,
            user_id=entity.user_id,
            start_time=entity.start_time,
            end_time=entity.end_time,
            title=entity.title,
            description=entity.description,
            attendees_count=entity.attendees_count,
            status=ReservationStatusModel(entity.status.value),
            approved_by_id=entity.approved_by_id,
            approved_at=entity.approved_at,
            rejection_reason=entity.rejection_reason,
            checked_in_at=entity.checked_in_at,
            checked_out_at=entity.checked_out_at,
            is_recurring=entity.is_recurring,
            recurrence_pattern=entity.recurrence_pattern,
            parent_reservation_id=entity.parent_reservation_id,
        )

class RuleMapper:
    @staticmethod
    def to_entity(model: RuleModel) -> ReservationRule:
        # Note: Time fields might need handling if they are None or specific format
        return ReservationRule(
            id=model.id,
            rule_type=RuleType(model.rule_type.value),
            name=model.name,
            resource_id=model.resource_id,
            description=model.description,
            day_of_week=model.day_of_week,
            start_time=model.start_time,
            end_time=model.end_time,
            start_date=model.start_date,
            end_date=model.end_date,
            max_reservations_per_day=model.max_reservations_per_day,
            max_reservations_per_week=model.max_reservations_per_week,
            max_hours_per_day=model.max_hours_per_day,
            max_hours_per_week=model.max_hours_per_week,
            is_active=model.is_active,
            priority=model.priority,
            created_at=model.created_at
        )

    @staticmethod
    def to_model(entity: ReservationRule) -> RuleModel:
        return RuleModel(
            id=entity.id,
            rule_type=RuleTypeModel(entity.rule_type.value),
            name=entity.name,
            resource_id=entity.resource_id,
            description=entity.description,
            day_of_week=entity.day_of_week,
            start_time=entity.start_time,
            end_time=entity.end_time,
            start_date=entity.start_date,
            end_date=entity.end_date,
            max_reservations_per_day=entity.max_reservations_per_day,
            max_reservations_per_week=entity.max_reservations_per_week,
            max_hours_per_day=entity.max_hours_per_day,
            max_hours_per_week=entity.max_hours_per_week,
            is_active=entity.is_active,
            priority=entity.priority,
        )
