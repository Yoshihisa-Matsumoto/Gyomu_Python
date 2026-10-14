# repository.py
from service.user.model import User


class UserRepository:
    def find_by_id(self, user_id: int) -> User | None:
        if user_id <= 0:
            return None

        return User(
            user_id=user_id,
            name=f"user-{user_id}",
        )
