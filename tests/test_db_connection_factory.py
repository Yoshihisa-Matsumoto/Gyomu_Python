from gyomu.db_connection_factory import DbConnectionFactory, GYOMU_COMMON_MAINDB_CONNECTION
from gyomu.exception import InvalidEnvironmentSetupError
import pytest
import os

def test_invalid_environment():
    with pytest.raises(InvalidEnvironmentSetupError) as ie:
        session = DbConnectionFactory.get_gyomu_db_session()
    print(ie.__str__())


def test_invalid_connection():
    os.environ[GYOMU_COMMON_MAINDB_CONNECTION] = 'aaab'
    with pytest.raises(InvalidEnvironmentSetupError) as ie:
        session = DbConnectionFactory.get_gyomu_db_session()
    print(ie.__str__())


