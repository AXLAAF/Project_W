"""
Tests for Reservations infrastructure mappers.
"""
from datetime import datetime
from unittest.mock import MagicMock
from app.domain.entities.reservations.resource import Resource
from app.domain.value_objects.reservations import ResourceType, ResourceStatus
from app.infrastructure.persistence.sqlalchemy.reservation_mappers import (
    ResourceMapper,
    ReservationMapper,
    RuleMapper
)

class TestResourceMapper:
    def test_to_entity(self):
        model = MagicMock()
        model.id = 1
        model.name = "Sala 1"
        model.code = "S1"
        model.resource_type.value = "SALA_CONFERENCIAS"
        model.status.value = "DISPONIBLE"
        model.is_active = True
        
        entity = ResourceMapper.to_entity(model)
        assert entity.id == 1
        assert entity.name == "Sala 1"
        assert entity.resource_type == ResourceType.SALA_CONFERENCIAS
        assert entity.status == ResourceStatus.DISPONIBLE

    def test_to_model(self):
        entity = Resource(name="Sala 1", code="S1", resource_type=ResourceType.EQUIPO)
        model = ResourceMapper.to_model(entity)
        assert model.name == "Sala 1"
        assert model.resource_type.value == "EQUIPO"

class TestReservationMapper:
    def test_to_entity(self):
        model = MagicMock()
        model.id = 1
        model.status.value = "PENDING"
        
        entity = ReservationMapper.to_entity(model)
        assert entity.id == 1
        assert entity.status.value == "PENDING"
