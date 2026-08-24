import json
import tomllib
from pathlib import Path

import pytest
import yaml
from gyomu_schema.config.config_loader_option import (
    EnvironmentLoaderOption,
    JsonLoaderOption,
    TomlLoaderOption,
    YamlLoaderOption,
)
from gyomu_schema.error.config import ConfigError
from pydantic import BaseModel
from returns.result import Failure, Success

from gyomu_infra.config.loader import ConfigLoader


class DummyConfig(BaseModel):
    name: str
    count: int
    enabled: bool


class TestConfigLoaderEnv:
    def test_load_from_environment(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("TEST_CONFIG_NAME", "example")
        monkeypatch.setenv("TEST_CONFIG_COUNT", "123")
        monkeypatch.setenv("TEST_CONFIG_ENABLED", "true")

        result = ConfigLoader.load(
            DummyConfig,
            EnvironmentLoaderOption(
                variables={
                    "TEST_CONFIG_NAME": "name",
                    "TEST_CONFIG_COUNT": "count",
                    "TEST_CONFIG_ENABLED": "enabled",
                }
            ),
        )

        assert result == Success(
            DummyConfig(
                name="example",
                count=123,
                enabled=True,
            )
        )

    def test_load_from_dot_env(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.delenv("TEST_CONFIG_NAME", raising=False)
        monkeypatch.delenv("TEST_CONFIG_COUNT", raising=False)
        monkeypatch.delenv("TEST_CONFIG_ENABLED", raising=False)

        env_path = tmp_path / ".env"
        env_path.write_text(
            """
            TEST_CONFIG_NAME=from-dot-env
            TEST_CONFIG_COUNT=456
            TEST_CONFIG_ENABLED=false
            """,
            encoding="utf-8",
        )

        result = ConfigLoader.load(
            DummyConfig,
            EnvironmentLoaderOption(
                variables={
                    "TEST_CONFIG_NAME": "name",
                    "TEST_CONFIG_COUNT": "count",
                    "TEST_CONFIG_ENABLED": "enabled",
                },
                use_dot_env=True,
                dot_env_path=env_path,
            ),
        )

        assert result == Success(
            DummyConfig(
                name="from-dot-env",
                count=456,
                enabled=False,
            )
        )

    def test_environment_variables_override_dot_env(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        env_path = tmp_path / ".env"
        env_path.write_text(
            """
            TEST_CONFIG_NAME=from-dot-env
            TEST_CONFIG_COUNT=456
            TEST_CONFIG_ENABLED=false
            """,
            encoding="utf-8",
        )

        monkeypatch.setenv(
            "TEST_CONFIG_NAME",
            "from-environment",
        )

        result = ConfigLoader.load(
            DummyConfig,
            EnvironmentLoaderOption(
                variables={
                    "TEST_CONFIG_NAME": "name",
                    "TEST_CONFIG_COUNT": "count",
                    "TEST_CONFIG_ENABLED": "enabled",
                },
                use_dot_env=True,
                dot_env_path=env_path,
            ),
        )

        assert result == Success(
            DummyConfig(
                name="from-environment",
                count=456,  # ← 実際のSchema定義に合わせる
                enabled=False,  # ← 実際のSchema定義に合わせる
            )
        )

    def test_load_returns_config_error_on_validation_failure(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("TEST_CONFIG_COUNT", "not-an-integer")

        result = ConfigLoader.load(
            DummyConfig,
            EnvironmentLoaderOption(
                variables={
                    "TEST_CONFIG_COUNT": "count",
                }
            ),
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, ConfigError)
        assert error.source == "env"
        assert error.phase == "validate"
        assert error.schema is DummyConfig


class TestConfigLoaderJson:
    def test_load_from_json(
        self,
        tmp_path: Path,
    ) -> None:
        config_path = tmp_path / "config.json"
        config_path.write_text(
            """
            {
                "name": "example",
                "count": 123,
                "enabled": true
            }
            """,
            encoding="utf-8",
        )

        result = ConfigLoader.load(
            DummyConfig,
            JsonLoaderOption(config_path),
        )

        assert result == Success(
            DummyConfig(
                name="example",
                count=123,
                enabled=True,
            )
        )

    def test_load_returns_config_error_on_invalid_json(
        self,
        tmp_path: Path,
    ) -> None:
        config_path = tmp_path / "config.json"
        config_path.write_text(
            "{ invalid json",
            encoding="utf-8",
        )

        result = ConfigLoader.load(
            DummyConfig,
            JsonLoaderOption(config_path),
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert error.source == "json"
        assert error.phase == "parse"
        assert isinstance(error.__cause__, json.JSONDecodeError)

    def test_load_returns_config_error_when_file_does_not_exist(
        self,
        tmp_path: Path,
    ) -> None:
        config_path = tmp_path / "not-found.json"

        result = ConfigLoader.load(
            DummyConfig,
            JsonLoaderOption(config_path),
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert error.source == "json"
        assert error.phase == "load"
        assert isinstance(error.__cause__, OSError)

    def test_load_returns_config_error_on_validation_failure(
        self,
        tmp_path: Path,
    ) -> None:
        config_path = tmp_path / "config.json"
        config_path.write_text(
            """
            {
                "name": "example",
                "count": 123
            }
            """,
            encoding="utf-8",
        )
        result = ConfigLoader.load(
            DummyConfig,
            JsonLoaderOption(config_path),
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, ConfigError)
        assert error.source == "json"
        assert error.phase == "validate"
        assert error.schema is DummyConfig


class TestConfigLoaderYaml:
    def test_load_from_yaml(
        self,
        tmp_path: Path,
    ) -> None:
        config_path = tmp_path / "config.yaml"
        config_path.write_text(
            """
            name: "example"
            count: 123
            enabled: true
            """,
            encoding="utf-8",
        )

        result = ConfigLoader.load(
            DummyConfig,
            YamlLoaderOption(config_path),
        )

        assert result == Success(
            DummyConfig(
                name="example",
                count=123,
                enabled=True,
            )
        )

    def test_load_returns_config_error_on_invalid_json(
        self,
        tmp_path: Path,
    ) -> None:
        config_path = tmp_path / "config.yaml"
        config_path.write_text(
            "{ invalid yaml",
            encoding="utf-8",
        )

        result = ConfigLoader.load(
            DummyConfig,
            YamlLoaderOption(config_path),
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert error.source == "yaml"
        assert error.phase == "parse"
        assert isinstance(error.__cause__, yaml.YAMLError)

    def test_load_returns_config_error_when_file_does_not_exist(
        self,
        tmp_path: Path,
    ) -> None:
        config_path = tmp_path / "not-found.yaml"

        result = ConfigLoader.load(
            DummyConfig,
            YamlLoaderOption(config_path),
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert error.source == "yaml"
        assert error.phase == "load"
        assert isinstance(error.__cause__, OSError)


class TestConfigLoaderToml:
    def test_load_from_toml(
        self,
        tmp_path: Path,
    ) -> None:
        config_path = tmp_path / "config.toml"
        config_path.write_text(
            """
            name = "example"
            count = 123
            enabled = true
            """,
            encoding="utf-8",
        )

        result = ConfigLoader.load(
            DummyConfig,
            TomlLoaderOption(config_path),
        )

        assert result == Success(
            DummyConfig(
                name="example",
                count=123,
                enabled=True,
            )
        )

    def test_load_returns_config_error_on_invalid_json(
        self,
        tmp_path: Path,
    ) -> None:
        config_path = tmp_path / "config.toml"
        config_path.write_text(
            "{ invalid toml",
            encoding="utf-8",
        )

        result = ConfigLoader.load(
            DummyConfig,
            TomlLoaderOption(config_path),
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert error.source == "toml"
        assert error.phase == "parse"
        assert isinstance(error.__cause__, tomllib.TOMLDecodeError)

    def test_load_returns_config_error_when_file_does_not_exist(
        self,
        tmp_path: Path,
    ) -> None:
        config_path = tmp_path / "not-found.toml"

        result = ConfigLoader.load(
            DummyConfig,
            TomlLoaderOption(config_path),
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert error.source == "toml"
        assert error.phase == "load"
        assert isinstance(error.__cause__, OSError)
