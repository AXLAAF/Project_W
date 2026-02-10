"""
Domain exceptions.
These exceptions are raised by domain logic and should be caught
by the application or interface layers to provide appropriate responses.
"""


class DomainError(Exception):
    """Base class for domain exceptions."""
    pass


class UserNotFoundError(DomainError):
    """Raised when a user is not found."""
    
    def __init__(self, identifier: str | int):
        self.identifier = identifier
        super().__init__(f"User not found: {identifier}")


class UserAlreadyExistsError(DomainError):
    """Raised when trying to create a user that already exists."""
    
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email '{email}' already exists")


class InvalidCredentialsError(DomainError):
    """Raised when authentication credentials are invalid."""
    
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message)


class InactiveUserError(DomainError):
    """Raised when an operation requires an active user but user is inactive."""
    
    def __init__(self, user_id: int | None = None):
        self.user_id = user_id
        message = f"User {user_id} is inactive" if user_id else "User is inactive"
        super().__init__(message)


class InvalidTokenError(DomainError):
    """Raised when a token is invalid or expired."""
    
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message)


class RoleNotFoundError(DomainError):
    """Raised when a role is not found."""
    
    def __init__(self, role_name: str):
        self.role_name = role_name
        super().__init__(f"Role not found: {role_name}")


class UserAlreadyInactiveError(DomainError):
    """Raised when trying to deactivate an already inactive user."""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User {user_id} is already inactive")
