"""
Unit tests for Internships domain entities and value objects.
"""
from datetime import date, datetime, timedelta
import pytest
from app.domain.entities.internship.company import Company
from app.domain.entities.internship.position import InternshipPosition
from app.domain.entities.internship.application import InternshipApplication
from app.domain.entities.internship.internship import Internship
from app.domain.entities.internship.report import InternshipReport
from app.domain.value_objects.internship import (
    ApplicationStatus,
    InternshipStatus,
    ReportType,
    ReportStatus,
    CompanyStatus,
    InternshipDuration,
)

class TestInternshipValueObjects:
    """Tests for internship value objects."""
    
    def test_internship_duration_valid(self):
        """Test valid duration calculation."""
        start = date(2024, 1, 1)
        end = date(2024, 1, 15)
        duration = InternshipDuration(start, end)
        assert duration.days == 14
        assert duration.weeks == 2
        
    def test_internship_duration_invalid(self):
        """Test invalid duration raises error."""
        start = date(2024, 1, 15)
        end = date(2024, 1, 1)
        with pytest.raises(ValueError):
            InternshipDuration(start, end)

class TestCompanyEntity:
    """Tests for Company entity."""
    
    def test_create_company(self):
        """Test creating a company."""
        company = Company(
            name="Tech Corp",
            rfc="TECH123456789",
            contact_email="contact@tech.com"
        )
        assert company.status == CompanyStatus.ACTIVE
        assert not company.is_verified
        assert not company.is_active  # Needs verification
        
    def test_verify_company(self):
        """Test verifying a company."""
        company = Company(
            name="Tech Corp",
            rfc="TECH123456789",
            contact_email="contact@tech.com"
        )
        company.verify()
        assert company.is_verified
        assert company.is_active

    def test_blacklist_company(self):
        """Test blacklisting a company."""
        company = Company(
            name="Bad Corp",
            rfc="BAD123",
            contact_email="bad@corp.com"
        )
        company.verify()
        company.blacklist()
        assert company.status == CompanyStatus.BLACKLISTED
        assert not company.is_active

class TestInternshipPositionEntity:
    """Tests for InternshipPosition entity."""
    
    def test_create_position(self):
        """Test creating a position."""
        position = InternshipPosition(
            company_id=1,
            title="Backend Dev",
            description="Python dev needed",
            requirements="Python, SQL",
            is_active=True
        )
        assert position.is_open
        
    def test_position_deadline(self):
        """Test position deadline logic."""
        future_date = date.today() + timedelta(days=30)
        past_date = date.today() - timedelta(days=1)
        
        pos_future = InternshipPosition(
            company_id=1,
            title="Dev",
            description="desc",
            requirements="reqs",
            application_deadline=future_date
        )
        assert pos_future.is_open
        
        pos_past = InternshipPosition(
            company_id=1,
            title="Dev",
            description="desc",
            requirements="reqs",
            application_deadline=past_date
        )
        assert not pos_past.is_open

class TestInternshipApplicationEntity:
    """Tests for InternshipApplication entity."""
    
    def test_create_application(self):
        """Test creating an application."""
        app = InternshipApplication(
            student_id=1,
            position_id=10
        )
        assert app.status == ApplicationStatus.PENDING
        assert app.is_pending
        
    def test_approve_application(self):
        """Test approving an application."""
        app = InternshipApplication(student_id=1, position_id=10)
        app.approve(reviewer_id=5, comments="Good fit")
        assert app.status == ApplicationStatus.APPROVED
        assert app.reviewed_by == 5
        assert not app.is_pending
        
    def test_reject_application(self):
        """Test rejecting an application."""
        app = InternshipApplication(student_id=1, position_id=10)
        app.reject(reviewer_id=5, comments="Not qualified")
        assert app.status == ApplicationStatus.REJECTED

class TestInternshipEntity:
    """Tests for Internship entity."""
    
    def test_create_internship(self):
        """Test creating an active internship."""
        internship = Internship(
            application_id=100,
            start_date=date(2024, 1, 1),
            expected_end_date=date(2024, 6, 1),
            supervisor_name="Jane Doe",
            supervisor_email="jane@company.com"
        )
        assert internship.status == InternshipStatus.ACTIVE
        assert internship.duration.weeks > 0
        
    def test_complete_internship(self):
        """Test completing an internship."""
        internship = Internship(
            application_id=100,
            start_date=date(2024, 1, 1),
            expected_end_date=date(2024, 6, 1),
            supervisor_name="Jane Doe",
            supervisor_email="jane@company.com"
        )
        end_date = date(2024, 6, 1)
        internship.complete(end_date, final_grade=9.5, certificate_path="/path/cert.pdf")
        
        assert internship.status == InternshipStatus.COMPLETED
        assert internship.actual_end_date == end_date
        assert internship.final_grade == 9.5
        
    def test_add_hours(self):
        """Test adding hours."""
        internship = Internship(
            application_id=100,
            start_date=date(2024, 1, 1),
            expected_end_date=date(2024, 6, 1),
            supervisor_name="Jane Doe",
            supervisor_email="jane@company.com"
        )
        internship.add_hours(40)
        assert internship.total_hours == 40
        
        with pytest.raises(ValueError):
            internship.add_hours(-5)

class TestInternshipReportEntity:
    """Tests for InternshipReport entity."""
    
    def test_create_report(self):
        """Test creating a report."""
        report = InternshipReport(
            internship_id=1,
            report_type=ReportType.PARTIAL,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 2, 1),
            content="Progress report",
            hours_logged=160
        )
        assert report.status == ReportStatus.PENDING
