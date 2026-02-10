"""
Grade value object.
Immutable value representing an academic grade.
"""
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Grade:
    """
    Grade value object.
    
    Represents an academic grade on a 0-10 scale.
    Includes letter grade conversion.
    """
    value: Decimal
    
    MIN_GRADE = Decimal("0.0")
    MAX_GRADE = Decimal("10.0")
    PASSING_GRADE = Decimal("6.0")
    
    def __post_init__(self):
        # Convert to Decimal if needed
        if not isinstance(self.value, Decimal):
            try:
                object.__setattr__(self, 'value', Decimal(str(self.value)))
            except (TypeError, ValueError):
                raise ValueError(f"Grade must be a number, got: {type(self.value)}")
        
        if self.value < self.MIN_GRADE:
            raise ValueError(f"Grade cannot be less than {self.MIN_GRADE}")
        
        if self.value > self.MAX_GRADE:
            raise ValueError(f"Grade cannot be more than {self.MAX_GRADE}")
    
    def __str__(self) -> str:
        return f"{self.value:.2f}"
    
    def __float__(self) -> float:
        return float(self.value)
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Grade):
            return self.value == other.value
        if isinstance(other, (int, float, Decimal)):
            return self.value == Decimal(str(other))
        return False
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __lt__(self, other) -> bool:
        if isinstance(other, Grade):
            return self.value < other.value
        if isinstance(other, (int, float, Decimal)):
            return self.value < Decimal(str(other))
        return NotImplemented
    
    @property
    def letter(self) -> str:
        """Convert numeric grade to letter grade."""
        if self.value >= Decimal("9.0"):
            return "A"
        elif self.value >= Decimal("8.0"):
            return "B"
        elif self.value >= Decimal("7.0"):
            return "C"
        elif self.value >= Decimal("6.0"):
            return "D"
        else:
            return "F"
    
    @property
    def is_passing(self) -> bool:
        """Check if grade is passing."""
        return self.value >= self.PASSING_GRADE
    
    @property
    def is_failing(self) -> bool:
        """Check if grade is failing."""
        return self.value < self.PASSING_GRADE
    
    @property
    def is_excellent(self) -> bool:
        """Check if grade is excellent (A)."""
        return self.value >= Decimal("9.0")
    
    @classmethod
    def from_letter(cls, letter: str) -> "Grade":
        """Create a Grade from a letter grade."""
        letter_to_value = {
            "A": Decimal("9.5"),
            "B": Decimal("8.5"),
            "C": Decimal("7.5"),
            "D": Decimal("6.5"),
            "F": Decimal("5.0"),
        }
        letter = letter.upper()
        if letter not in letter_to_value:
            raise ValueError(f"Invalid letter grade: {letter}")
        return cls(letter_to_value[letter])
