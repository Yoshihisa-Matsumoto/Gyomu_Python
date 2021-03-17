from sys import platform
import getpass

from gyomu.user_windows import _WindowsUser


class UserFactory:
    _current_user: 'User' = None

    @staticmethod
    def get_current_user() -> 'User':
        if UserFactory._current_user != None:
            return UserFactory._current_user

        uid = getpass.getuser()


        if platform == "win32":
            UserFactory._current_user = _WindowsUser(uid)
        elif platform == "linux" or platform == "linux2":
            return None
        return UserFactory._current_user



