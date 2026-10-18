from dataclasses import dataclass


@dataclass
class User:
    name: str
    age: int


class UserWithoutDataclass:
    name: str
    age: int
