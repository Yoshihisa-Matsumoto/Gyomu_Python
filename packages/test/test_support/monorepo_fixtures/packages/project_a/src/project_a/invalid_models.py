from dataclasses import dataclass


@dataclass(frozen=True)
class InvalidModel:
    """Represent a summarized user."""

    user_id = "1"
    address = "ABC"
    age: int
