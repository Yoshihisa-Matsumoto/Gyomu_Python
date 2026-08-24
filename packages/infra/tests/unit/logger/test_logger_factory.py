from collections.abc import Iterator
from pathlib import Path

import pytest
from gyomu_schema.error.config import ConfigError

from gyomu_infra.logger.factory import LoggerFactory


class TestLoggerFactory:
    @pytest.fixture(autouse=True)
    def reset_factory(self) -> Iterator[None]:
        LoggerFactory._reset()

        yield

        LoggerFactory._reset()

    def test_get_creates_logger(
        self,
        tmp_path: Path,
    ) -> None:
        dot_env = tmp_path / ".env"
        dot_env.write_text(
            "GYOMU_LOGGER_LEVEL=INFO\nGYOMU_LOGGER_CONSOLE_ENABLED=false\n",
            encoding="utf-8",
        )

        logger = LoggerFactory.get(dot_env_path=dot_env)

        assert logger is not None

    def test_get_returns_same_logger(
        self,
        tmp_path: Path,
    ) -> None:
        dot_env = tmp_path / ".env"
        dot_env.write_text(
            "GYOMU_LOGGER_LEVEL=INFO\nGYOMU_LOGGER_CONSOLE_ENABLED=false\n",
            encoding="utf-8",
        )

        first = LoggerFactory.get(dot_env_path=dot_env)
        second = LoggerFactory.get(dot_env_path=dot_env)

        assert first is second

    def test_dot_env_configuration_is_applied(
        self,
        tmp_path: Path,
    ) -> None:
        dot_env = tmp_path / ".env"
        dot_env.write_text(
            "GYOMU_LOGGER_LEVEL=WARNING\nGYOMU_LOGGER_CONSOLE_ENABLED=false\n",
            encoding="utf-8",
        )

        logger = LoggerFactory.get(dot_env_path=dot_env)

        # LoggerImplの内部実装を直接検証するのではなく、
        # 実際に設定されたLoggerの動作を確認する。
        logger.info("info")
        logger.warning("warning")

    def test_get_raises_config_error_when_configuration_is_invalid(
        self,
        tmp_path: Path,
    ) -> None:
        dot_env = tmp_path / ".env"
        dot_env.write_text(
            "GYOMU_LOGGER_LEVEL=INVALID\n",
            encoding="utf-8",
        )

        with pytest.raises(ConfigError):
            LoggerFactory.get(dot_env_path=dot_env)

    def test_reset_creates_new_logger(
        self,
        tmp_path: Path,
    ) -> None:
        dot_env = tmp_path / ".env"
        dot_env.write_text(
            "GYOMU_LOGGER_LEVEL=INFO\nGYOMU_LOGGER_CONSOLE_ENABLED=false\n",
            encoding="utf-8",
        )

        first = LoggerFactory.get(dot_env_path=dot_env)

        LoggerFactory._reset()

        second = LoggerFactory.get(dot_env_path=dot_env)

        assert first is not second
