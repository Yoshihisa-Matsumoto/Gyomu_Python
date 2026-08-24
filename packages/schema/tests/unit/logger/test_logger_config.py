from pathlib import Path

import pytest
from gyomu_schema.logger.config import LoggerConfig, LogLevel
from pydantic import ValidationError as PydanticValidationError


class TestLoggerConfig:
    def test_default_values(self) -> None:
        config = LoggerConfig()

        assert config.level == LogLevel.INFO
        assert config.console_enabled is True
        assert config.log_directory is None
        assert config.log_filename is None
        assert config.timestamped_filename is True

    def test_all_values(self) -> None:
        config = LoggerConfig(
            level=LogLevel.DEBUG,
            console_enabled=False,
            log_directory=Path("/var/log/gyomu"),
            log_filename="application.log",
            timestamped_filename=True,
        )

        assert config.level == LogLevel.DEBUG
        assert config.console_enabled is False
        assert config.log_directory == Path("/var/log/gyomu")
        assert config.log_filename == "application.log"
        assert config.timestamped_filename is True

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("DEBUG", LogLevel.DEBUG),
            ("INFO", LogLevel.INFO),
            ("WARNING", LogLevel.WARNING),
            ("ERROR", LogLevel.ERROR),
            ("CRITICAL", LogLevel.CRITICAL),
        ],
    )
    def test_level_accepts_string(
        self,
        value: str,
        expected: LogLevel,
    ) -> None:
        config = LoggerConfig.model_validate(
            {"level": value},
        )

        assert config.level == expected

    def test_invalid_level(self) -> None:
        with pytest.raises(PydanticValidationError):
            LoggerConfig.model_validate(
                {"level": "INVALID"},
            )

    def test_log_directory_accepts_path(self) -> None:
        config = LoggerConfig(
            log_directory=Path("/var/log/gyomu"),
        )

        assert config.log_directory == Path("/var/log/gyomu")

    def test_log_directory_accepts_string(self) -> None:
        config = LoggerConfig(
            log_directory=Path("/var/log/gyomu"),
        )

        assert config.log_directory == Path("/var/log/gyomu")

    def test_log_filename_can_be_none(self) -> None:
        config = LoggerConfig(log_filename=None)

        assert config.log_filename is None

    def test_log_filename_accepts_string(self) -> None:
        config = LoggerConfig(log_filename="gyomu.log")

        assert config.log_filename == "gyomu.log"

    def test_timestamped_filename(self) -> None:
        config = LoggerConfig(
            log_filename="gyomu.log",
            timestamped_filename=True,
        )

        assert config.timestamped_filename is True
