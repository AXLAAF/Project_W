"""
Role domain entity.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from enum import Enum


class RoleType(str, Enum):
    """Enumeration of system roles."""
    ALUMNO = "ALUMNO"
    PROFESOR = "PROFESOR"
    COORDINADOR = "COORDINADOR"
    ADMIN_RECURSOS = "ADMIN_RECURSOS"
    GESTOR_PRACTICAS = "GESTOR_PRACTICAS"
    ADMIN_SISTEMA = "ADMIN_SISTEMA"



@dataclass
class Role:
    """Role domain entity."""
    name: str
    description: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def __str__(self) -> str:
        return self.name
