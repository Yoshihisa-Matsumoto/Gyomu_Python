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
        pass

    @property
    @abstractmethod
    def get_members(self):
        pass

    @property
    @abstractmethod
    def userid(self) -> str:
        pass

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
