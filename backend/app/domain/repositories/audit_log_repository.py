"""
Audit log repository interface (port).
Defines the contract for audit log persistence operations.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Sequence, Tuple

from app.domain.entities.audit_log import AuditLog, AuditAction


class IAuditLogRepository(ABC):
    """
    Abstract interface for audit log repository.
    
    This is a 'port' in hexagonal architecture terminology.
    """
    
    @abstractmethod
    async def save(self, audit_log: AuditLog) -> AuditLog:
        """
        Save a new audit log entry.
        
        Args:
            audit_log: The audit log entity to save
        
        Returns:
            The saved audit log with generated ID
        """
        pass
    
    @abstractmethod
    async def get_by_user(
        self,
        user_id: int,
        offset: int = 0,
        limit: int = 50,
    ) -> Tuple[Sequence[AuditLog], int]:
        """
        Get audit logs for a specific user.
        
        Args:
            user_id: The user's ID
            offset: Number of records to skip
            limit: Maximum records to return
        
        Returns:
            Tuple of (list of audit logs, total count)
        """
        pass
    
    @abstractmethod
    async def get_by_action(
        self,
        action: AuditAction,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Tuple[Sequence[AuditLog], int]:
        """
        Get audit logs filtered by action type and date range.
        
        Args:
            action: The audit action type
            start_date: Optional start date filter
            end_date: Optional end date filter
            offset: Number of records to skip
            limit: Maximum records to return
        
        Returns:
            Tuple of (list of audit logs, total count)
        """
        pass
    
    @abstractmethod
    async def get_by_entity(
        self,
        entity_type: str,
        entity_id: int,
        offset: int = 0,
        limit: int = 50,
    ) -> Tuple[Sequence[AuditLog], int]:
        """
        Get audit logs for a specific entity.
        
        Args:
            entity_type: Type of the entity (e.g., "User", "Subject")
            entity_id: ID of the entity
            offset: Number of records to skip
            limit: Maximum records to return
        
        Returns:
            Tuple of (list of audit logs, total count)
        """
        pass
