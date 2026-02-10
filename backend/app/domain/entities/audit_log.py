"""
Audit log domain entity.
Pure domain model for tracking user actions.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class AuditAction(str, Enum):
    """Types of auditable actions."""
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"
    USER_CREATE = "USER_CREATE"
    USER_UPDATE = "USER_UPDATE"
    USER_DEACTIVATE = "USER_DEACTIVATE"
    USER_ACTIVATE = "USER_ACTIVATE"
    ROLE_ASSIGN = "ROLE_ASSIGN"
    ROLE_REMOVE = "ROLE_REMOVE"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    PASSWORD_RESET = "PASSWORD_RESET"
    PROFILE_UPDATE = "PROFILE_UPDATE"
    ENROLLMENT_CREATE = "ENROLLMENT_CREATE"
    ENROLLMENT_UPDATE = "ENROLLMENT_UPDATE"
    RESERVATION_CREATE = "RESERVATION_CREATE"
    RESERVATION_CANCEL = "RESERVATION_CANCEL"
    INTERNSHIP_APPLY = "INTERNSHIP_APPLY"
    INTERNSHIP_APPROVE = "INTERNSHIP_APPROVE"


@dataclass
class AuditLog:
    """
    Audit log domain entity.
    
    Tracks all significant user actions in the system.
    """
    action: AuditAction
    user_id: Optional[int] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    @classmethod
    def create(
        cls,
        action: AuditAction,
        user_id: Optional[int] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> "AuditLog":
        """Factory method to create a new audit log entry."""
        return cls(
            action=action,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.now(),
        )
