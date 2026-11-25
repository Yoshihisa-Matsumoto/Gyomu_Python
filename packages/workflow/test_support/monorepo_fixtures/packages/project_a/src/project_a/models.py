from dataclasses import dataclass


@dataclass(frozen=True)
class UserSummary:
    """Represent a summarized user."""

    user_id: int
    display_name: str


@dataclass(frozen=True)
class AdvancedUserSummary(UserSummary):
    email: str


class User:
    """Represent a user entity."""

    def __init__(self, user_id: int, name: str) -> None:
        self.user_id = user_id
        self.name = name


UserId = int
