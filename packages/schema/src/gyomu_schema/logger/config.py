from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LoggerConfig(BaseModel):
    level: LogLevel = LogLevel.INFO
    console_enabled: bool = True

    log_directory: Path | None = None
    log_filename: str | None = None
    timestamped_filename: bool = True
