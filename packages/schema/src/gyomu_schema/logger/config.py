from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel


class LogLevel(StrEnum):
    """Logging level enumeration."""

    DEBUG = "DEBUG"
    """Debug log level."""

    INFO = "INFO"
    """Info log level."""

    WARNING = "WARNING"
    """Warning log level."""

    ERROR = "ERROR"
    """Error log level."""

    CRITICAL = "CRITICAL"
    """Critical log level."""


class LoggerConfig(BaseModel):
    """Configuration settings for the logger."""

    level: LogLevel = LogLevel.INFO
    """Logging level."""

    console_enabled: bool = True
    """Whether console logging is enabled."""

    log_directory: Path | None = None
    """Directory where log files are stored."""

    log_filename: str | None = None
    """Filename for log files."""

    timestamped_filename: bool = True
    """Whether to append a timestamp to log filenames."""
