from abc import ABCMeta, abstractmethod
from sys import platform


class User(metaclass=ABCMeta):
    @property
    @abstractmethod
    def groups(self):
        pass

    @property
    @abstractmethod
    def is_group(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_valid(self) -> bool:
        return False

    @property
    @abstractmethod
    def get_members(self):
        pass

    @property
    def userid(self) -> str:
        return self._user_id

    def __eq__(self, other):
        if other is not None:
            return other.userid == self.userid
        return False

    @abstractmethod
    def is_in_member(self, group_user: 'User') -> bool:
        pass

    @property
    @abstractmethod
    def region(selfself) -> str:
        return ""

    _user_id: str

    def __init__(self, user_id: str):
        self._user_id = user_id

class DummyUser(User):

    @property
    def groups(self):
        pass

    @property
    def is_group(self) -> bool:
        pass

    @property
    def is_valid(self) -> bool:
        return False

    @property
    def members(self):
        pass

    @property
    def user_id(self):
        return super().userid


    def is_in_member(self, group_user: User) -> bool:
        pass

    def _init_group(self):
        pass

    def __init__(self, user_id: str):
        super().__init__(user_id)

    @property
    def region(self) ->str:
        pass

    @property
    def get_members(self):
        pass