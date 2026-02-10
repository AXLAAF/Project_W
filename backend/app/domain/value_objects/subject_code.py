"""
SubjectCode value object.
Immutable value representing a subject code.
"""
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class SubjectCode:
    """
    Subject code value object.
    
    Format: Department prefix (2-4 letters) + Number (3-4 digits)
    Example: MAT101, CS1234, FIS210
    """
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Subject code cannot be empty")
        
        # Normalize to uppercase
        object.__setattr__(self, 'value', self.value.upper().strip())
        
        # Validate format (letters followed by numbers)
        pattern = r'^[A-Z]{2,4}\d{3,4}$'
        if not re.match(pattern, self.value):
            # Allow more flexible codes
            if len(self.value) < 3 or len(self.value) > 20:
                raise ValueError(f"Invalid subject code format: {self.value}")
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, SubjectCode):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other.upper()
        return False
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    @property
    def department_prefix(self) -> str:
        """Extract department prefix from code."""
        # Get all leading letters
        prefix = ""
        for char in self.value:
            if char.isalpha():
                prefix += char
            else:
                break
        return prefix
    
    @property
    def number(self) -> str:
        """Extract number portion from code."""
        # Get all trailing digits
        number = ""
        for char in reversed(self.value):
            if char.isdigit():
                number = char + number
            else:
                break
        return number
