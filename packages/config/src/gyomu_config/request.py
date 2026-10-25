from pathlib import Path
from typing import Protocol

from gyomu_schema.error.config import ConfigError
from pydantic import BaseModel
from returns.result import Result


class ConfigPathResolver[C](Protocol):
    def get_path(self, context: C) -> Result[Path, ConfigError]: ...


class ConfigRequest[T: BaseModel, C]:
    def __init__(
        self,
        config_type: type[T],
        context: C,
        path_resolver: ConfigPathResolver[C],
    ) -> None:
        self.config_type = config_type
        self.context = context
        self.path_resolver = path_resolver
