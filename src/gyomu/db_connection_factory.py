import os
from enum import Enum
from sqlalchemy import create_engine, engine
from sqlalchemy.orm import Session

# from src.gyomu import Session


GYOMU_COMMON_MAINDB_TYPE: str = "GYOMU_COMMON_MAINDB_TYPE"
GYOMU_COMMON_MAINDB_CONNECTION: str = "GYOMU_COMMON_MAINDB_CONNECTION"


class DbType(Enum):
    MSSQL = 1,
    POSTGRESQL = 2,
    Other = 99


class DbConnectionFactory:

    @classmethod
    def get_sqldb_type(cls) -> DbType:
        env_value = os.environ[GYOMU_COMMON_MAINDB_TYPE]
        if env_value == "":
            raise ValueError("Environment Variable GYOMU_COMMON_MAINDB_TYPE not set")
        try:
            return DbType[env_value]
        except:
            return DbType.Other

    @classmethod
    def __get_gyomu_db_engine(cls) -> engine:
        try:
            env_value = os.environ[GYOMU_COMMON_MAINDB_CONNECTION]
            return create_engine(env_value)
        except:
            return None

    @classmethod
    def get_gyomu_db_session(cls) -> Session:
        _engine: engine = cls.__get_gyomu_db_engine()
        if _engine is None:
            raise ValueError("Connection String is not set")
        return Session(_engine, future=True)
