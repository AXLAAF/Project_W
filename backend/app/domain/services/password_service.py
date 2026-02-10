"""
Password Service Interface.
"""
from abc import ABC, abstractmethod


class IPasswordService(ABC):
    """Interface for password hashing and verification."""

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Hash a plain text password."""
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        pass
