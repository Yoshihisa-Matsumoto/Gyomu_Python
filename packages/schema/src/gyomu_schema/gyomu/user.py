from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """Represents a user with a unique user identifier."""

    user_id: str
    """The unique identifier for the user."""
