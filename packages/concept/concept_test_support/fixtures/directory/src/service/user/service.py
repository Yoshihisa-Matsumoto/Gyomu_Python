# service.py
from service.user.model import User
from service.user.repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def find_user(self, user_id: int) -> User | None:
        return self._repository.find_by_id(user_id)
