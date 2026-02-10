"""
Credits value object.
Immutable value representing academic credits.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Credits:
    """
    Credits value object.
    
    Represents academic credits for a subject.
    Valid range: 1-12 credits (configurable).
    """
    value: int
    
    MIN_CREDITS = 1
    MAX_CREDITS = 12
    
    def __post_init__(self):
        if not isinstance(self.value, int):
            try:
                object.__setattr__(self, 'value', int(self.value))
            except (TypeError, ValueError):
                raise ValueError(f"Credits must be an integer, got: {type(self.value)}")
        
        if self.value < self.MIN_CREDITS:
            raise ValueError(f"Credits cannot be less than {self.MIN_CREDITS}")
        
        if self.value > self.MAX_CREDITS:
            raise ValueError(f"Credits cannot be more than {self.MAX_CREDITS}")
    
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
            return Credits(min(self.value + other.value, self.MAX_CREDITS))
        if isinstance(other, int):
            return Credits(min(self.value + other, self.MAX_CREDITS))
        raise TypeError(f"Cannot add Credits with {type(other)}")
    
    def __lt__(self, other) -> bool:
        if isinstance(other, Credits):
            return self.value < other.value
        if isinstance(other, int):
            return self.value < other
        return NotImplemented
    
    def __le__(self, other) -> bool:
        if isinstance(other, Credits):
            return self.value <= other.value
        if isinstance(other, int):
            return self.value <= other
        return NotImplemented
