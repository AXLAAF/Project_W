"""
Role Repository Interface.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.role import Role


class IRoleRepository(ABC):
    """Interface for Role repository."""
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        pass
    
    @abstractmethod
    async def get_by_id(self, role_id: int) -> Optional[Role]:
        """Get role by ID."""
        pass
    
    @abstractmethod
    async def list_roles(self) -> List[Role]:
        """List all roles."""
        pass

    @abstractmethod
    async def get_or_create(self, role_name: str, description: Optional[str] = None) -> Role:
        """Get or create a role."""
        pass

    @abstractmethod
    async def assign_to_user(self, user_id: int, role: Role, assigned_by: Optional[int] = None) -> None:
        """Assign role to user."""
        pass
