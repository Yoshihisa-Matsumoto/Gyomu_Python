from abc import ABCMeta, abstractmethod
from sys import platform

class User(metaclass=ABCMeta):

    @abstractmethod
    def get_groups(self):
        pass

    @abstractmethod
    def is_group(self) -> bool:
        pass

    @abstractmethod
    def is_valid(self) -> bool:
        pass

    @abstractmethod
    def get_members(self):
        pass

    @abstractmethod
    def get_userid(self):
        pass

    def __eq__(self, other):
        if other is not None:
            return other.get_userid() == self.get_userid()
        return False

    @abstractmethod
    def is_in_member(self, group_user: 'User') -> bool:
        pass

    @abstractmethod
    def get_region(selfself) ->str:
        return ""


