from abc import ABCMeta, abstractmethod
from gyomu.user import User
from gyomu.user_factory import UserFactory
import socket
import os

class Configurator(metaclass=ABCMeta):
    GYOMU_COMMON_MODE: str = "GYOMU_COMMON_MODE"

    @abstractmethod
    def get_machine_name(self) ->str:
        pass

    @abstractmethod
    def get_address(self):
        pass

    @abstractmethod
    def get_username(self) ->str:
        pass

    @abstractmethod
    def get_unique_instance_id_per_machine(self) ->int:
        pass

    @abstractmethod
    def get_region(self) ->str:
        pass

    @abstractmethod
    def get_user(self) -> User:
        pass

    @abstractmethod
    def get_mode(self) -> str:
        pass

    @abstractmethod
    def get_application_id(self) -> int:
        pass

    @abstractmethod
    def set_application_id(self, application_id: int) :
        pass


class BaseConfigurator(Configurator):

    _user: User = None
    def __init__(self, user: User = None):
        if user is None:
            user = UserFactory.get_current_user()

        self._user=user
        self.init()

    def init(self):
        self._machine_name=socket.gethostname()
        self._ip_address = str(socket.gethostbyname(self._machine_name))
        self._process_id = os.getpid()

    _machine_name: str
    _ip_address:str
    _process_id: int

    def get_machine_name(self) ->str:
        return self._machine_name

    def get_address(self):
        return self._ip_address

    def get_username(self) ->str:
        return self._user.get_userid()

    def get_unique_instance_id_per_machine(self) ->int:
        return self._process_id

    def get_region(self) ->str:
        return self._user.get_region()

    def get_user(self) -> User:
        return self._user

    def get_mode(self) -> str:
        return os.environ[Configurator.GYOMU_COMMON_MODE]

    _application_id:int = 0

    def get_application_id(self) -> int:
        return self._application_id

    def set_application_id(self, application_id: int) :
        self._application_id=application_id
