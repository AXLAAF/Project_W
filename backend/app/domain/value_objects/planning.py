"""
Value objects for Planning domain.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
import re


@dataclass(frozen=True)
class SubjectCode:
    """
    Subject code value object.
    Immutable identifier for a subject (e.g., "MAT101", "CS-201").
    """
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Subject code cannot be empty")
        
        # Normalize: strip and uppercase
        object.__setattr__(self, 'value', self.value.strip().upper())
        
        if len(self.value) > 20:
            raise ValueError("Subject code cannot exceed 20 characters")
        
        # Allow alphanumeric with optional dashes
        if not re.match(r'^[A-Z0-9][A-Z0-9\-]*$', self.value):
            raise ValueError("Subject code must be alphanumeric (dashes allowed)")
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, SubjectCode):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other.strip().upper()
        return False
    
    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class Credits:
    """
    Credits value object.
    Represents academic credits for a subject.
    """
    value: int
    
    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Credits cannot be negative")
        if self.value > 20:
            raise ValueError("Credits cannot exceed 20")
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __int__(self) -> int:
        return self.value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Credits):
            return self.value == other.value
        if isinstance(other, int):
            return self.value == other
        return False
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __add__(self, other: "Credits") -> "Credits":
        if isinstance(other, Credits):
            return Credits(self.value + other.value)
        if isinstance(other, int):
            return Credits(self.value + other)
        raise TypeError(f"Cannot add Credits with {type(other)}")


@dataclass(frozen=True)
class Grade:
    """
    Grade value object.
    Represents a numeric grade (0.00 - 10.00 scale).
    """
    value: Decimal
    
    def __post_init__(self):
        if isinstance(self.value, (int, float)):
            object.__setattr__(self, 'value', Decimal(str(self.value)))
        
        if self.value < 0:
            raise ValueError("Grade cannot be negative")
        if self.value > 10:
            raise ValueError("Grade cannot exceed 10")
        
        # Round to 2 decimal places
        object.__setattr__(self, 'value', self.value.quantize(Decimal('0.01')))
    
    @property
    def letter(self) -> str:
        """Get letter grade equivalent."""
        v = float(self.value)
        if v >= 9.0:
            return "A"
        elif v >= 8.0:
            return "B"
        elif v >= 7.0:
            return "C"
        elif v >= 6.0:
            return "D"
        else:
            return "F"
    
    @property
    def is_passing(self) -> bool:
        """Check if grade is passing (6.0 or above)."""
        return self.value >= Decimal('6.0')
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __float__(self) -> float:
        return float(self.value)
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Grade):
            return self.value == other.value
        if isinstance(other, (Decimal, int, float)):
            return self.value == Decimal(str(other))
        return False
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __lt__(self, other: "Grade") -> bool:
        if isinstance(other, Grade):
            return self.value < other.value
        return self.value < Decimal(str(other))
    
    def __le__(self, other: "Grade") -> bool:
        if isinstance(other, Grade):
            return self.value <= other.value
        return self.value <= Decimal(str(other))


@dataclass(frozen=True)
class PeriodCode:
    """
    Academic period code value object.
    Format: "YYYY-N" where N is period number (e.g., "2026-1", "2026-2").
    """
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Period code cannot be empty")
        
        object.__setattr__(self, 'value', self.value.strip())
        
        # Validate format
        if not re.match(r'^\d{4}-[1-9]$', self.value):
            raise ValueError("Period code must be in format 'YYYY-N' (e.g., '2026-1')")
    
    @property
    def year(self) -> int:
        """Extract year from period code."""
        return int(self.value.split('-')[0])
    
    @property
    def period_number(self) -> int:
        """Extract period number from code."""
        return int(self.value.split('-')[1])
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, PeriodCode):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other.strip()
        return False
    
    def __hash__(self) -> int:
        return hash(self.value)
