"""
Email value object.
"""
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Email:
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Email cannot be empty")
        # Simple regex for validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.value):
            raise ValueError(f"Invalid email format: {self.value}")
    
    def __str__(self) -> str:
        return self.value
