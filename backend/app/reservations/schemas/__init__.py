"""Reservations schemas package."""
from .resource import (
    ResourceBase,
    ResourceCreate,
    ResourceUpdate,
    ResourceRead,
    ResourceList,
)
from .reservation import (
    ReservationBase,
    ReservationCreate,
    ReservationUpdate,
    ReservationApprove,
    ReservationReject,
    ReservationCheckIn,
    ReservationCheckOut,
    ReservationRead,
    ReservationWithResource,
    ReservationCalendarItem,
    ResourceSummary,
)
from .rule_sanction import (
    RuleBase,
    RuleCreate,
    RuleUpdate,
    RuleRead,
    SanctionBase,
    SanctionCreate,
    SanctionResolve,
    SanctionRead,
)

__all__ = [
    # Resource
    "ResourceBase",
    "ResourceCreate",
    "ResourceUpdate",
    "ResourceRead",
    "ResourceList",
    # Reservation
    "ReservationBase",
    "ReservationCreate",
    "ReservationUpdate",
    "ReservationApprove",
    "ReservationReject",
    "ReservationCheckIn",
    "ReservationCheckOut",
    "ReservationRead",
    "ReservationWithResource",
    "ReservationCalendarItem",
    "ResourceSummary",
    # Rule
    "RuleBase",
    "RuleCreate",
    "RuleUpdate",
    "RuleRead",
    # Sanction
    "SanctionBase",
    "SanctionCreate",
    "SanctionResolve",
    "SanctionRead",
]
