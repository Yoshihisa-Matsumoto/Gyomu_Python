from pydantic import BaseModel, Field


class User(BaseModel):
    """User information."""

    id: int = Field(description="Primary identifier")

    @classmethod
    def create(cls, name: str) -> "User":
        """Create a user."""
        return cls(id=1)
