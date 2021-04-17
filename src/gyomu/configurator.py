import multiprocessing
from abc import ABCMeta, abstractmethod
from gyomu.user import User
from gyomu.user_factory import UserFactory
import socket
import os
from multiprocessing import Manager
from multiprocessing.managers import SyncManager, BaseProxy
import inspect
import traceback
from enum import Enum


class SharedObjectType(Enum):
    Dictionary = 1,
    List = 2,
    Lock = 3,
    Condition = 4


class ManagedObjectFactory:
    _manager = None

    def create_dictionary(self):
        if self._manager is not None:
            return self._manager.dict()
        return ConfigurationFactory.get_instance()._get_manager().dict()

    def create_lock(self):
        if self._manager is not None:
            return self._manager.Lock()
        return ConfigurationFactory.get_instance()._get_manager().Lock()

    def create_condition(self):
        if self._manager is not None:
            return self._manager.Condition()
        return ConfigurationFactory.get_instance()._get_manager().Condition()


class ManagedObjectFactoryProxy(BaseProxy):
    _exposed_ = (
        '__getattribute__', '__setattr__', '__delattr__', 'create_dictionary', 'create_lock', 'create_condition')

    def __getattr__(self, key):
        if key[0] == '_':
            return object.__getattribute__(self, key)
        callmethod = object.__getattribute__(self, '_callmethod')
        return callmethod('__getattribute__', (key,))

    def __setattr__(self, key, value):
        if key[0] == '_':
            return object.__setattr__(self, key, value)
        callmethod = object.__getattribute__(self, '_callmethod')
        return callmethod('__setattr__', (key, value))

    def __delattr__(self, key):
        if key[0] == '_':
            return object.__delattr__(self, key)
        callmethod = object.__getattribute__(self, '_callmethod')
        return callmethod('__delattr__', (key,))

    def create_dictionary(self):
        callmethod = object.__getattribute__(self, '_callmethod')
        return callmethod('create_dictionary')

    def create_lock(self):
        callmethod = object.__getattribute__(self, '_callmethod')
        return callmethod('create_lock')

    def create_condition(self):
        callmethod = object.__getattribute__(self, '_callmethod')
        return callmethod('create_condition')


class Configurator(metaclass=ABCMeta):
    GYOMU_COMMON_MODE: str = "GYOMU_COMMON_MODE"
    GLOBAL_LOCK_KEY: str = "!!!!Configurator:Lock!####"
    GLOBAL_MANAGER_PROXY: str = "!!!Configurator:ManagerControl!###"
    GLOBAL_APPLICATION_ID_KEY: str = "!!!Configurator:ApplicationID!###"

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

    @property
    @abstractmethod
    def shared_dictionary(self) -> dict:
        pass

    def retrieve_shared_item_and_register_if_not_exist(self, keyword: str, object_type: SharedObjectType):
        frame = inspect.stack()[1]
        fileparts = frame.filename.split(os.path.sep)
        filename = fileparts[len(fileparts) - 1]
        # function = frame.function
        key = filename + '!' + keyword
        with self._retrieve_global_lock():
            # print('Before:' + str(self.shared_dictionary))
            if self.shared_dictionary.get(key) is None:
                # print('create shared item :' + key)
                if object_type == SharedObjectType.Lock:
                    self.shared_dictionary[key] = self._get_manager().Lock()
                elif object_type == SharedObjectType.List:
                    self.shared_dictionary[key] = self._get_manager().list()
                elif object_type == SharedObjectType.Dictionary:
                    self.shared_dictionary[key] = self._get_manager().dict()
                elif object_type == SharedObjectType.Condition:
                    self.shared_dictionary[key] = self._get_manager().Condition()

            # print('After:' + str(self.shared_dictionary))
            return self.shared_dictionary.get(key)

    def _retrieve_global_lock(self):
        return self.shared_dictionary[self.GLOBAL_LOCK_KEY]

    def dump_shared_dictionary(self):
        return str(self.shared_dictionary)

    def get_proxy_object(self) -> ManagedObjectFactory:
        return self.shared_dictionary[self.GLOBAL_MANAGER_PROXY]

    @abstractmethod
    def _get_manager(self):
        pass


class _BaseConfigurator(Configurator):
    _user: User = None

    def __init__(self, user: User = None, shared_dictionary: dict = None):
        if user is None:
            user = UserFactory.get_current_user()

        self._user = user
        self.init(shared_dictionary)

    __manager: Manager

    def init(self, shared_dictionary: dict):
        self._machine_name = socket.gethostname()
        self._ip_address = str(socket.gethostbyname(self._machine_name))
        self._process_id = os.getpid()

        self.__manager = Manager()
        if shared_dictionary is None:
            shared_dictionary = self.__manager.dict()
            shared_dictionary[Configurator.GLOBAL_LOCK_KEY] = self.__manager.Lock()
            proxy = self.__manager.ManagedObjectFactory()
            proxy._manager = self.__manager
            shared_dictionary[Configurator.GLOBAL_MANAGER_PROXY] = proxy
        else:
            self._application_id = shared_dictionary[Configurator.GLOBAL_APPLICATION_ID_KEY]
        self._shared_dictionary = shared_dictionary

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
        self._shared_dictionary[Configurator.GLOBAL_APPLICATION_ID_KEY] = application_id

    _shared_dictionary: dict = None

    @property
    def shared_dictionary(self) -> dict:
        return self._shared_dictionary

    def _get_manager(self):
        return self.__manager


class ConfigurationFactory:
    __config: Configurator = None

    @staticmethod
    def get_instance(shared_dictionary: dict = None) -> Configurator:
        # print('PID:' + str(os.getpid()) + ' Config generated. __config Exist?' + str(ConfigurationFactory.__config is not None))
        if ConfigurationFactory.__config is None:
            SyncManager.register('ManagedObjectFactory', ManagedObjectFactory, ManagedObjectFactoryProxy)
        if ConfigurationFactory.__config is None or shared_dictionary is not None:
            ConfigurationFactory.__config = _BaseConfigurator(shared_dictionary=shared_dictionary)

        return ConfigurationFactory.__config
