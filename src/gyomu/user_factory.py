from sys import platform
import getpass

from gyomu.user_windows import _WindowsUser
from gyomu.user import DummyUser, User


class UserFactory:
    _current_user: 'User' = None

    @staticmethod
    def get_current_user() -> 'User':
        if UserFactory._current_user is not None:
            return UserFactory._current_user

        uid = getpass.getuser()

        if platform == "win32":
            UserFactory._current_user = _WindowsUser(uid)
        elif platform == "linux" or platform == "linux2":
            return None
        return UserFactory._current_user

    @staticmethod
    def get_user(user_id: str) -> 'User':
        return DummyUser(user_id)
