from dataclasses import dataclass
from pathlib import Path

from gyomu_infra.filesystem.file_io import get_file_stat
from gyomu_schema.error.config import ConfigError
from pydantic import BaseModel
from returns.result import Failure, Result, Success

from gyomu_config.cache.base import _ConfigCache


@dataclass(frozen=True)
class FileState:
    mtime_ns: int
    size: int


@dataclass(frozen=True)
class FileConfigCacheKey:
    path: Path
    config_type: type[BaseModel]


class FileCacheValidator:
    def get_state(
        self,
        key: FileConfigCacheKey,
    ) -> Result[FileState | None, ConfigError]:
        stat_result = get_file_stat(key.path)
        if isinstance(stat_result, Failure):
            return stat_result.alt(
                lambda error: ConfigError(
                    message="fail to get file state", phase="load", source="json"
                ).chain(error)
            )
        stat = stat_result.unwrap()
        if stat is None:
            return Success(stat)

        return Success(
            FileState(
                mtime_ns=stat.st_mtime_ns,
                size=stat.st_size,
            )
        )

    def is_valid(
        self,
        cached_state: FileState,
        current_state: FileState,
    ) -> bool:
        return cached_state == current_state


class FileConfigCache[T: BaseModel](_ConfigCache[T, FileConfigCacheKey, FileState]):
    def __init__(self) -> None:
        super().__init__(FileCacheValidator())
