import json
import logging
import tempfile
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path

from gyomu_schema.logger.config import LoggerConfig
from gyomu_schema.logger.logger import Logger


class LoggerImpl(Logger):
    def __init__(self, config: LoggerConfig) -> None:
        self._logger = logging.getLogger("gyomu")
        self._logger.setLevel(config.level.value)
        self._logger.propagate = False

        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

        if config.console_enabled:
            self._add_console_handler(self._logger, formatter)

        if config.log_filename is not None:
            self._add_file_handler(config, formatter)

    def debug(
        self,
        message: str,
        *args: object,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        self._logger.debug(
            self._format_message(message, extra),
            *args,
        )

    def info(
        self,
        message: str,
        *args: object,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        self._logger.info(
            self._format_message(message, extra),
            *args,
        )

    def warning(
        self,
        message: str,
        *args: object,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        self._logger.warning(
            self._format_message(message, extra),
            *args,
        )

    def error(
        self,
        message: str,
        *args: object,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        self._logger.error(
            self._format_message(message, extra),
            *args,
        )

    def critical(
        self,
        message: str,
        *args: object,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        self._logger.critical(
            self._format_message(message, extra),
            *args,
        )

    def exception(
        self,
        message: str,
        *args: object,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        self._logger.exception(
            self._format_message(message, extra),
            *args,
        )

    @staticmethod
    def _format_message(
        message: str,
        extra: Mapping[str, object] | None,
    ) -> str:
        if extra is None:
            return message

        return f"{message} {json.dumps(dict(extra), default=str)}"

    @staticmethod
    def _add_console_handler(
        logger: logging.Logger,
        formatter: logging.Formatter,
    ) -> None:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def _add_file_handler(
        self,
        config: LoggerConfig,
        formatter: logging.Formatter,
    ) -> None:
        directory = config.log_directory or Path(tempfile.gettempdir())
        directory.mkdir(parents=True, exist_ok=True)

        filename = config.log_filename
        assert filename is not None

        if config.timestamped_filename:
            filename = self._add_timestamp(filename)

        handler = logging.FileHandler(
            directory / filename,
            encoding="utf-8",
        )
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    @staticmethod
    def _add_timestamp(filename: str) -> str:
        path = Path(filename)
        timestamp = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")

        if path.suffix:
            return f"{path.stem}_{timestamp}{path.suffix}"

        return f"{filename}_{timestamp}"
