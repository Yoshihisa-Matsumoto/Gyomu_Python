import os
from enum import Enum
from sqlalchemy import create_engine

GYOMU_COMMON_MAINDB_TYPE: str = "GYOMU_COMMON_MAINDB_TYPE"
GYOMU_COMMON_MAINDB_CONNECTION: str = "GYOMU_COMMON_MAINDB_CONNECTION"

class DbType(Enum):
    MSSQL = 1,
    POSTGRESQL = 2,
    Other = 99


class DbConnectionFactory:

    @classmethod
    def get_sqldb_type(cls) -> DbType:
        try:
            env_value = os.environ[GYOMU_COMMON_MAINDB_TYPE]
            return DbType[env_value]
        except:
            return DbType.Other

    @classmethod
    def get_gyomu_db_connection(cls):
        try:
            env_value=os.environ[GYOMU_COMMON_MAINDB_CONNECTION]
            return create_engine(env_value)
        except:
            return None


