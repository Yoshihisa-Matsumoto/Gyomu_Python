import logging
from pathlib import Path

from gyomu_schema.config.config_loader_option import EnvironmentLoaderOption
from gyomu_schema.logger.config import LoggerConfig
from gyomu_schema.logger.logger import Logger
from returns.result import Failure

from gyomu_infra.config.loader import ConfigLoader
from gyomu_infra.logger.impl import LoggerImpl


class LoggerFactory:
    """Factory for the application-wide logger.

    The logger is initialized lazily on the first call to :meth:`get` and
    reused for subsequent calls.

    Gyomu Context:
        Logger configuration is loaded from the environment through
        :class:`ConfigLoader` and converted to :class:`LoggerConfig` before
        the :class:`LoggerImpl` is created.

        The logger is initialized only once and shared throughout the
        application. The ``dot_env_path`` argument of :meth:`get` exists
        primarily to allow tests to specify an explicit ``.env`` file.
        In normal application use, it should be omitted so that the default
        ``.env`` location is used.

        :meth:`_reset` is provided for test isolation. It clears the cached
        logger so that the factory can be initialized again with different
        configuration in another test. It should not be used by application
        code.
    """

    _logger: Logger | None = None

    @classmethod
    def get(cls, dot_env_path: Path | None = None) -> Logger:
        if cls._logger is None:
            cls._logger = cls._create(dot_env_path)

        return cls._logger

    @classmethod
    def _create(cls, dot_env_path: Path | None = None) -> Logger:
        config = ConfigLoader.load(
            LoggerConfig,
            EnvironmentLoaderOption(
                use_dot_env=True,
                dot_env_path=dot_env_path,
                variables={
                    "GYOMU_LOGGER_LEVEL": "level",
                    "GYOMU_LOGGER_CONSOLE_ENABLED": "console_enabled",
                    "GYOMU_LOGGER_DIRECTORY": "log_directory",
                    "GYOMU_LOGGER_FILENAME": "log_filename",
                    "GYOMU_LOGGER_TIMESTAMPLED_FILENAME": "timestamped_filename",
                },
            ),
        )

        if isinstance(config, Failure):
            raise config.failure()

        return LoggerImpl(config.unwrap())

    @classmethod
    def _reset(cls) -> None:
        if cls._logger is None:
            return

        logger = logging.getLogger("gyomu")

        for handler in logger.handlers:
            handler.close()

        logger.handlers.clear()
        cls._logger = None
