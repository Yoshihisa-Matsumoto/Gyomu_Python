class GyomuError(Exception):
    """Base class for Gyomu application errors."""


class GyomuIOError(GyomuError):
    """I/O related error."""


class DatabaseError(GyomuIOError):
    """Database access error."""


class ValidationError(GyomuError):
    """Validation error."""
