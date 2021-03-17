from gyomu.db_connection_factory import DbConnectionFactory, GYOMU_COMMON_MAINDB_TYPE, DbType, GYOMU_COMMON_MAINDB_CONNECTION
import pytest
import os


def test_get_sqldb_type():
    os.environ[GYOMU_COMMON_MAINDB_TYPE] = DbType.POSTGRESQL.name
    assert DbType.POSTGRESQL == DbConnectionFactory.get_sqldb_type()

def test_sqldb_setting_nonexist():
    os.environ[GYOMU_COMMON_MAINDB_TYPE] = ""
    with pytest.raises(ValueError):
        db_type= DbConnectionFactory.get_sqldb_type()
