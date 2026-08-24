from pathlib import Path

import pytest
from dotenv import load_dotenv
from gyomu_schema.config.config_loader_option import EnvironmentLoaderOption
from gyomu_schema.error.config import ConfigError
from sqlalchemy import Engine

from gyomu_infra.db.connection.factory import DbConnectionFactory

load_dotenv()


@pytest.fixture
def db_engine(project_dot_env: Path) -> Engine:
    try:
        return DbConnectionFactory.create_engine(
            option=EnvironmentLoaderOption(
                use_dot_env=True,
                dot_env_path=project_dot_env,
                variables={"GYOMU_COMMON_MAINDB_CONNECTION": "connection_string"},
            )
        )
    except ConfigError:
        pytest.skip("GYOMU_COMMON_MAINDB_CONNECTION is not configured")
