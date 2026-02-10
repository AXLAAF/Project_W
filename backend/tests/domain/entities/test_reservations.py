"""
Tests for Reservations domain entities.
"""
import pytest
from datetime import datetime, timedelta
from app.domain.entities.reservations.resource import Resource, ResourceStatus
from app.domain.entities.reservations.reservation import Reservation, ReservationStatus
from app.domain.entities.reservations.rule import ReservationRule
from app.domain.value_objects.reservations import ResourceType, RuleType, TimeSlot

class TestResource:
    def test_resource_creation(self):
        resource = Resource(
            name="Sala 1",
            code="S1",
            resource_type=ResourceType.SALA_CONFERENCIAS,
            capacity=10
        )
        assert resource.name == "Sala 1"
        assert resource.status == ResourceStatus.DISPONIBLE
        assert resource.is_active

    def test_resource_availability(self):
        # Case 1: Active and Available
        r1 = Resource(name="R1", code="R1", resource_type=ResourceType.EQUIPO)
        assert r1.is_available()

        # Case 2: Maintenance
        r1.set_maintenance()
        assert not r1.is_available()
        assert r1.status == ResourceStatus.MANTENIMIENTO

        # Case 3: Inactive
        r1.set_available()
        r1.is_active = False
        assert not r1.is_available()

class TestTimeSlot:
    def test_timeslot_creation(self):
        start = datetime(2024, 1, 1, 10, 0)
        end = datetime(2024, 1, 1, 12, 0)
        slot = TimeSlot(start, end)
        assert slot.duration_minutes == 120

    def test_timeslot_invalid(self):
        start = datetime(2024, 1, 1, 12, 0)
        end = datetime(2024, 1, 1, 10, 0)
        with pytest.raises(ValueError):
            TimeSlot(start, end)

    def test_timeslot_overlap(self):
        base = TimeSlot(datetime(2024, 1, 1, 10, 0), datetime(2024, 1, 1, 12, 0))
        
        # Overlap inside
        t1 = TimeSlot(datetime(2024, 1, 1, 10, 30), datetime(2024, 1, 1, 11, 30))
        assert base.overlaps(t1)

        # No overlap
        t2 = TimeSlot(datetime(2024, 1, 1, 12, 0), datetime(2024, 1, 1, 13, 0))
        assert not base.overlaps(t2)

class TestReservation:
    def test_reservation_creation(self):
        res = Reservation(
            resource_id=1,
            user_id=1,
            start_time=datetime(2024, 1, 1, 10, 0),
            end_time=datetime(2024, 1, 1, 12, 0),
            title="Meeting"
        )
        assert res.status == ReservationStatus.PENDING
        assert res.time_slot.duration_minutes == 120

    def test_reservation_approve(self):
        res = Reservation(1, 1, datetime.now(), datetime.now(), "T")
        res.approve(approver_id=5)
        assert res.status == ReservationStatus.APPROVED
        assert res.approved_by_id == 5
        assert res.approved_at is not None

    def test_reservation_cancel(self):
        res = Reservation(1, 1, datetime.now(), datetime.now(), "T")
        res.cancel()
        assert res.status == ReservationStatus.CANCELLED

class TestReservationRule:
    def test_rule_applies(self):
        # Global rule
        r1 = ReservationRule(RuleType.HORARIO, "Global", resource_id=None)
        assert r1.applies_to_resource(1)
        assert r1.applies_to_resource(99)

        # Specific rule
        r2 = ReservationRule(RuleType.HORARIO, "Specific", resource_id=10)
        assert r2.applies_to_resource(10)
        assert not r2.applies_to_resource(11)
