"""
Unit tests for Internship infrastructure mappers.
"""
from datetime import datetime, date
from unittest.mock import MagicMock
from app.domain.entities.internship.company import Company
from app.domain.entities.internship.position import InternshipPosition
from app.domain.value_objects.internship import ApplicationStatus, InternshipStatus
from app.infrastructure.persistence.sqlalchemy.internship_mappers import (
    CompanyMapper,
    PositionMapper,
    ApplicationMapper,
    InternshipMapper,
)

class TestCompanyMapper:
    def test_to_entity(self):
        model = MagicMock()
        model.id = 1
        model.name = "Tech Corp"
        model.rfc = "RFC123"
        model.is_active = True
        model.is_verified = True
        
        entity = CompanyMapper.to_entity(model)
        assert entity.id == 1
        assert entity.name == "Tech Corp"
        assert entity.is_active

    def test_to_model(self):
        entity = Company(name="Tech", rfc="RFC", contact_email="e@mail.com")
        model = CompanyMapper.to_model(entity)
        assert model.name == "Tech"
        assert model.rfc == "RFC"

class TestPositionMapper:
    def test_to_entity(self):
        model = MagicMock()
        model.id = 1
        model.title = "Dev"
        model.is_active = True
        
        entity = PositionMapper.to_entity(model)
        assert entity.id == 1
        assert entity.title == "Dev"
        assert entity.is_active

class TestApplicationMapper:
    def test_to_entity(self):
        model = MagicMock()
        model.id = 1
        model.status.value = "pending"
        
        entity = ApplicationMapper.to_entity(model)
        assert entity.id == 1
        assert entity.status == ApplicationStatus.PENDING

class TestInternshipMapper:
    def test_to_entity(self):
        model = MagicMock()
        model.id = 1
        model.status.value = "active"
        
        entity = InternshipMapper.to_entity(model)
        assert entity.id == 1
        assert entity.status == InternshipStatus.ACTIVE
