"""
Internships module Pydantic schemas.
"""
from app.internships.schemas.company import (
    CompanyBase,
    CompanyCreate,
    CompanyUpdate,
    CompanyRead,
    CompanyList,
)
from app.internships.schemas.position import (
    PositionBase,
    PositionCreate,
    PositionUpdate,
    PositionRead,
    PositionWithCompany,
)
from app.internships.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationRead,
    ApplicationWithDetails,
)
from app.internships.schemas.internship import (
    InternshipCreate,
    InternshipUpdate,
    InternshipRead,
    InternshipWithReports,
)
from app.internships.schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportRead,
)

__all__ = [
    # Company
    "CompanyBase",
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyRead",
    "CompanyList",
    # Position
    "PositionBase",
    "PositionCreate",
    "PositionUpdate",
    "PositionRead",
    "PositionWithCompany",
    # Application
    "ApplicationCreate",
    "ApplicationUpdate",
    "ApplicationRead",
    "ApplicationWithDetails",
    # Internship
    "InternshipCreate",
    "InternshipUpdate",
    "InternshipRead",
    "InternshipWithReports",
    # Report
    "ReportCreate",
    "ReportUpdate",
    "ReportRead",
]
