"""Example module for docstring update integration testing."""

from collections.abc import Sequence

DEFAULT_NAME = "unknown"


UserId = int


class User:
    name: str
    user_id: UserId

    class Metadata:
        key: str

        def __init__(self, key: str) -> None:
            self.key = key

    MetadataType = Metadata

    def __init__(self, user_id: UserId, name: str) -> None:
        self.user_id = user_id
        self.name = name

    def rename(self, name: str) -> None:
        self.name = name

    def get_name(self) -> str:
        return self.name


def create_user(user_id: UserId, name: str) -> User:
    return User(user_id, name)


def find_user(users: Sequence[User], user_id: UserId) -> User | None:
    for user in users:
        if user.user_id == user_id:
            return user

    return None
