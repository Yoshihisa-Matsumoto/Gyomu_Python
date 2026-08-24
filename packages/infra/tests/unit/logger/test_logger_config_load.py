from pathlib import Path

from gyomu_schema.config.config_loader_option import EnvironmentLoaderOption
from gyomu_schema.logger.config import LoggerConfig, LogLevel
from returns.result import Failure, Success

from gyomu_infra.config.loader import ConfigLoader


class TestConfigLoaderLoggerConfig:
    def test_load_from_environment(
        self,
        monkeypatch,
    ) -> None:
        monkeypatch.setenv("GYOMU_LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("GYOMU_LOG_CONSOLE_ENABLED", "false")
        monkeypatch.setenv(
            "GYOMU_LOG_DIRECTORY",
            "/var/log/gyomu",
        )
        monkeypatch.setenv("GYOMU_LOG_FILENAME", "gyomu.log")
        monkeypatch.setenv(
            "GYOMU_LOG_TIMESTAMPED_FILENAME",
            "true",
        )

        result = ConfigLoader.load(
            LoggerConfig,
            EnvironmentLoaderOption(
                variables={
                    "GYOMU_LOG_LEVEL": "level",
                    "GYOMU_LOG_CONSOLE_ENABLED": "console_enabled",
                    "GYOMU_LOG_DIRECTORY": "log_directory",
                    "GYOMU_LOG_FILENAME": "log_filename",
                    "GYOMU_LOG_TIMESTAMPED_FILENAME": "timestamped_filename",
                },
            ),
        )
        assert isinstance(result, Success)
        config = result.unwrap()

        assert config.level == LogLevel.DEBUG
        assert config.console_enabled is False
        assert config.log_directory == Path("/var/log/gyomu")
        assert config.log_filename == "gyomu.log"
        assert config.timestamped_filename is True

    def test_invalid_level_returns_config_error(
        self,
        monkeypatch,
    ) -> None:
        monkeypatch.setenv("GYOMU_LOG_LEVEL", "INVALID")

        result = ConfigLoader.load(
            LoggerConfig,
            EnvironmentLoaderOption(
                variables={
                    "GYOMU_LOG_LEVEL": "level",
                },
            ),
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert error.source == "env"
        assert error.phase == "validate"
