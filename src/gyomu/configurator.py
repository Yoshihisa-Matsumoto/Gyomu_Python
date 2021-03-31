from abc import ABCMeta, abstractmethod
from gyomu.user import User
from gyomu.user_factory import UserFactory
import socket
import os


class Configurator(metaclass=ABCMeta):
    GYOMU_COMMON_MODE: str = "GYOMU_COMMON_MODE"

    @property
    @abstractmethod
    def machine_name(self) -> str:
        pass

    @property
    @abstractmethod
    def address(self):
        pass

    @property
    @abstractmethod
    def username(self) -> str:
        pass

    @property
    @abstractmethod
    def unique_instance_id_per_machine(self) -> int:
        pass

    @property
    @abstractmethod
    def region(self) -> str:
        pass

    @property
    @abstractmethod
    def user(self) -> User:
        pass

    @property
    @abstractmethod
    def mode(self) -> str:
        pass

    @property
    @abstractmethod
    def application_id(self) -> int:
        pass

    @abstractmethod
    def set_application_id(self, application_id: int):
        pass


class BaseConfigurator(Configurator):
    _user: User = None

    def __init__(self, user: User = None):
        if user is None:
            user = UserFactory.get_current_user()

        self._user = user
        self.init()

    def init(self):
        self._machine_name = socket.gethostname()
        self._ip_address = str(socket.gethostbyname(self._machine_name))
        self._process_id = os.getpid()

    _machine_name: str
    _ip_address: str
    _process_id: int

    @property
    def machine_name(self) -> str:
        return self._machine_name

    @property
    def address(self):
        return self._ip_address

    @property
    def username(self) -> str:
        return self._user.userid

    @property
    def unique_instance_id_per_machine(self) -> int:
        return self._process_id

    @property
    def region(self) -> str:
        return self._user.region

    @property
    def user(self) -> User:
        return self._user

    @property
    def mode(self) -> str:
        return os.environ[Configurator.GYOMU_COMMON_MODE]

    _application_id: int = 0

    @property
    def application_id(self) -> int:
        return self._application_id

    def set_application_id(self, application_id: int):
        self._application_id = application_id
