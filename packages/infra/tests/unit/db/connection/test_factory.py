from unittest.mock import patch

import pytest
from gyomu_schema.config.config_loader_option import EnvironmentLoaderOption
from gyomu_schema.error import ConfigError
from sqlalchemy import Engine
from sqlalchemy.exc import SQLAlchemyError

from gyomu_infra.db.connection.factory import (
    GYOMU_COMMON_MAINDB_CONNECTION,
    DbConnectionFactory,
)


def test_create_engine_from_environment_variable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connection_string = "sqlite://"

    monkeypatch.setenv(
        GYOMU_COMMON_MAINDB_CONNECTION,
        connection_string,
    )

    engine = DbConnectionFactory.create_engine(
        option=EnvironmentLoaderOption(
            use_dot_env=False,
            variables={"GYOMU_COMMON_MAINDB_CONNECTION": "connection_string"},
        )
    )

    assert isinstance(engine, Engine)

    engine.dispose()


def test_create_engine_fails_when_connection_string_is_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(
        GYOMU_COMMON_MAINDB_CONNECTION,
        raising=False,
    )

    with pytest.raises(ConfigError) as exc_info:
        DbConnectionFactory.create_engine(
            option=EnvironmentLoaderOption(
                use_dot_env=False,
                variables={"GYOMU_COMMON_MAINDB_CONNECTION": "connection_string"},
            )
        )

    assert exc_info.value.context == "ConfigLoader._validate"


def test_create_engine_passes_connection_string_to_sqlalchemy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connection_string = "sqlite://"

    monkeypatch.setenv(
        GYOMU_COMMON_MAINDB_CONNECTION,
        connection_string,
    )

    with patch("gyomu_infra.db.connection.factory.create_engine") as create_engine:
        DbConnectionFactory.create_engine(
            option=EnvironmentLoaderOption(
                use_dot_env=False,
                variables={"GYOMU_COMMON_MAINDB_CONNECTION": "connection_string"},
            )
        )

        create_engine.assert_called_once_with(connection_string)


def test_create_engine_converts_sqlalchemy_error_to_config_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connection_string = "invalid://connection"

    monkeypatch.setenv(
        GYOMU_COMMON_MAINDB_CONNECTION,
        connection_string,
    )

    original_error = SQLAlchemyError("invalid connection string")

    with (
        patch(
            "gyomu_infra.db.connection.factory.create_engine",
            side_effect=original_error,
        ),
        pytest.raises(ConfigError) as exc_info,
    ):
        DbConnectionFactory.create_engine(
            option=EnvironmentLoaderOption(
                use_dot_env=False,
                variables={"GYOMU_COMMON_MAINDB_CONNECTION": "connection_string"},
            )
        )

    error = exc_info.value

    assert error.context == "DbConnectionFactory.create_engine"
    assert error.__cause__ is original_error
