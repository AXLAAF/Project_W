"""Domain services interfaces package."""
from app.domain.services.password_service import IPasswordService
from app.domain.services.token_service import ITokenService

__all__ = ["IPasswordService", "ITokenService"]
