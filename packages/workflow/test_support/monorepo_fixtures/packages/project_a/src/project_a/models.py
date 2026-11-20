from dataclasses import dataclass

from pydantic import BaseModel, Field


class UserModel(BaseModel):
    """Represent a user."""

    user_id: int
    name: str
    email: str | None = None


class UserCreateModel(BaseModel):
    """Represent user creation input."""

    name: str = Field(min_length=1)
    email: str


@dataclass(frozen=True)
class UserSummary:
    """Represent a summarized user."""

    user_id: int
    display_name: str


class User:
    """Represent a user entity."""

    def __init__(self, user_id: int, name: str) -> None:
        self.user_id = user_id
        self.name = name


UserId = int
