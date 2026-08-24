import logging
from collections.abc import Iterator
from pathlib import Path

import pytest
from gyomu_schema.logger.config import LoggerConfig, LogLevel

from gyomu_infra.logger.impl import LoggerImpl


@pytest.fixture
def gyomu_logger() -> Iterator[None]:
    logger = logging.getLogger("gyomu")

    for handler in logger.handlers:
        handler.close()

    logger.handlers.clear()

    yield

    for handler in logger.handlers:
        handler.close()

    logger.handlers.clear()


class TestLoggerImpl:
    def test_console_logging(
        self,
        gyomu_logger: None,
        capsys,
    ) -> None:
        logger = LoggerImpl(
            LoggerConfig(
                console_enabled=True,
            )
        )

        logger.info("Hello")

        captured = capsys.readouterr()

        assert "[INFO] Hello" in captured.err

    def test_console_logging_can_be_disabled(
        self,
        gyomu_logger: None,
        capsys,
    ) -> None:
        logger = LoggerImpl(
            LoggerConfig(
                console_enabled=False,
            )
        )

        logger.info("Hello")

        captured = capsys.readouterr()

        assert captured.out == ""
        assert captured.err == ""

    def test_log_level(
        self,
        capsys,
        gyomu_logger: None,
    ) -> None:
        logger = LoggerImpl(
            LoggerConfig(
                level=LogLevel.WARNING,
            )
        )

        logger.debug("debug")
        logger.info("info")
        logger.warning("warning")
        logger.error("error")
        logger.critical("critical")

        captured = capsys.readouterr()

        assert "[DEBUG] debug" not in captured.err
        assert "[INFO] info" not in captured.err
        assert "[WARNING] warning" in captured.err
        assert "[ERROR] error" in captured.err
        assert "[CRITICAL] critical" in captured.err

    def test_string_formatting(self, gyomu_logger: None, capsys) -> None:
        logger = LoggerImpl(
            LoggerConfig(),
        )

        logger.info("Processing file: %s", "test.txt")

        captured = capsys.readouterr()

        assert "[INFO] Processing file: test.txt" in captured.err

    def test_extra(self, gyomu_logger: None, capsys) -> None:
        logger = LoggerImpl(
            LoggerConfig(),
        )

        logger.info(
            "Processing completed",
            extra={
                "file": "test.txt",
                "count": 10,
            },
        )

        captured = capsys.readouterr()

        assert "[INFO] Processing completed" in captured.err
        assert '"file": "test.txt"' in captured.err
        assert '"count": 10' in captured.err

    def test_file_logging(self, gyomu_logger: None, tmp_path: Path) -> None:
        log_file = tmp_path / "gyomu.log"

        logger = LoggerImpl(
            LoggerConfig(
                console_enabled=False,
                log_directory=tmp_path,
                log_filename="gyomu.log",
                timestamped_filename=False,
            )
        )

        logger.info("Hello")

        content = log_file.read_text(encoding="utf-8")

        assert "[INFO] Hello" in content

    def test_file_logging_with_timestamp(
        self,
        gyomu_logger: None,
        tmp_path: Path,
    ) -> None:
        logger = LoggerImpl(
            LoggerConfig(
                console_enabled=False,
                log_directory=tmp_path,
                log_filename="gyomu.log",
                timestamped_filename=True,
            )
        )

        logger.info("Hello")

        files = list(tmp_path.glob("gyomu_*.log"))

        assert len(files) == 1

        content = files[0].read_text(encoding="utf-8")

        assert "[INFO] Hello" in content

    def test_file_logging_uses_temp_directory_when_directory_is_none(
        self,
        gyomu_logger: None,
        monkeypatch,
        tmp_path: Path,
    ) -> None:
        monkeypatch.setattr(
            "gyomu_infra.logger.impl.tempfile.gettempdir",
            lambda: str(tmp_path),
        )

        logger = LoggerImpl(
            LoggerConfig(
                console_enabled=False,
                log_filename="gyomu.log",
                timestamped_filename=False,
            )
        )

        logger.info("Hello")

        log_file = tmp_path / "gyomu.log"

        assert log_file.exists()

        content = log_file.read_text(encoding="utf-8")

        assert "[INFO] Hello" in content

    def test_exception(self, gyomu_logger: None, capsys) -> None:
        logger = LoggerImpl(
            LoggerConfig(),
        )

        try:
            raise ValueError("Something went wrong")
        except ValueError:
            logger.exception("Processing failed")

        captured = capsys.readouterr()

        assert "[ERROR] Processing failed" in captured.err
        assert "ValueError: Something went wrong" in captured.err
