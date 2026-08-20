import pytest
from dotenv import load_dotenv
from gyomu_schema.error.config import ConfigError
from sqlalchemy import Engine

from gyomu_infra.db.connection.factory import DbConnectionFactory

load_dotenv()


@pytest.fixture
def db_engine() -> Engine:
    try:
        return DbConnectionFactory.create_engine()
    except ConfigError:
        pytest.skip("GYOMU_COMMON_MAINDB_CONNECTION is not configured")
