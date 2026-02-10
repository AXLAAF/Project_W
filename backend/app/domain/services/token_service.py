"""
Token Service Interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import timedelta


class ITokenService(ABC):
    """Interface for token generation and validation."""

    @abstractmethod
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create an access token."""
        pass
    
    @abstractmethod
    def create_refresh_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a refresh token."""
        pass

    @abstractmethod
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate a token."""
        pass
        
    @abstractmethod
    def verify_token_type(self, payload: Dict[str, Any], token_type: str) -> bool:
        """Verify token type claim."""
        pass
