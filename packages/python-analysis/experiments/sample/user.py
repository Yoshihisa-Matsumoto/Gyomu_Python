from pydantic import BaseModel, Field

Version = 1.2


class User(BaseModel):
    """User information."""

    id: int = Field(description="Primary identifier")

    @classmethod
    def create(cls, name: str) -> "User":
        """Create a user."""
        return cls(id=1)
