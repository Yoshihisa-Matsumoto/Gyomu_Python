import os
from enum import Enum
from sqlalchemy import create_engine, engine
from sqlalchemy.orm import Session
from gyomu.exception import InvalidEnvironmentSetupError
# from src.gyomu import Session


GYOMU_COMMON_MAINDB_CONNECTION: str = "GYOMU_COMMON_MAINDB_CONNECTION"


class DbConnectionFactory:

    @classmethod
    def __get_gyomu_db_engine(cls) -> engine:
        if os.environ.get(GYOMU_COMMON_MAINDB_CONNECTION) is None:
            raise InvalidEnvironmentSetupError('Environment Variable GYOMU_COMMON_MAINDB_CONNECTION is not setup')
        try:
            env_value = os.environ[GYOMU_COMMON_MAINDB_CONNECTION]
            return create_engine(env_value)
        except Exception as ex:
            raise InvalidEnvironmentSetupError("using DB Engine is not installed or connection string is invalid\n" + ex.__str__())

    @classmethod
    def get_gyomu_db_session(cls) -> Session:
        _engine: engine = cls.__get_gyomu_db_engine()
        if _engine is None:
            raise ValueError("Connection String is not set")
        return Session(_engine, future=True)
