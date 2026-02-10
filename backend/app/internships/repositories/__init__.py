"""
Internships module repositories.
"""
from app.internships.repositories.company_repository import CompanyRepository
from app.internships.repositories.position_repository import PositionRepository
from app.internships.repositories.application_repository import ApplicationRepository
from app.internships.repositories.internship_repository import InternshipRepository

__all__ = [
    "CompanyRepository",
    "PositionRepository",
    "ApplicationRepository",
    "InternshipRepository",
]
