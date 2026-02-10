"""
Reservations domain value objects.
"""
from enum import Enum, unique
from dataclasses import dataclass
from datetime import datetime, time, date

@unique
class ResourceType(str, Enum):
    """Types of reservable resources."""
    SALA_CONFERENCIAS = "SALA_CONFERENCIAS"
    LABORATORIO = "LABORATORIO"
    AUDITORIO = "AUDITORIO"
    SALA_ESTUDIO = "SALA_ESTUDIO"
    EQUIPO = "EQUIPO"
    VEHICULO = "VEHICULO"
    OTRO = "OTRO"

@unique
class ResourceStatus(str, Enum):
    """Resource availability status."""
    DISPONIBLE = "DISPONIBLE"
    MANTENIMIENTO = "MANTENIMIENTO"
    FUERA_SERVICIO = "FUERA_SERVICIO"

@unique
class ReservationStatus(str, Enum):
    """Status of a reservation."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"

@unique
class RuleType(str, Enum):
    """Types of reservation rules."""
    HORARIO = "HORARIO"              # Operating hours
    BLOQUEO = "BLOQUEO"              # Blocked time slots
    LIMITE_USUARIO = "LIMITE_USUARIO"  # User reservation limits
    ANTICIPACION = "ANTICIPACION"     # Advance booking requirements

@dataclass(frozen=True)
class TimeSlot:
    """Value object representing a time slot."""
    start_time: datetime
    end_time: datetime

    def __post_init__(self):
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time")

    @property
    def duration_minutes(self) -> int:
        """Calculate duration in minutes."""
        return int((self.end_time - self.start_time).total_seconds() / 60)

    def overlaps(self, other: "TimeSlot") -> bool:
        """Check if this time slot overlaps with another."""
        return self.start_time < other.end_time and self.end_time > other.start_time
