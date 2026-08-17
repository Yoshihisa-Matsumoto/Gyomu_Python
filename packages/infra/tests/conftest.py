from dotenv import load_dotenv
import os

import pytest
from sqlalchemy import Engine, create_engine

load_dotenv()

@pytest.fixture
def db_engine() -> Engine:
    connection = os.getenv("GYOMU_COMMON_MAINDB_CONNECTION")

    if connection is None:
        pytest.skip(
            "GYOMU_COMMON_MAINDB_CONNECTION is not configured"
        )

    return create_engine(connection)
