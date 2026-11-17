from pathlib import Path
from unittest.mock import Mock

from gyomu_config.cache.file import (
    FileCacheValidator,
    FileConfigCache,
    FileConfigCacheKey,
    FileState,
)
from gyomu_infra.filesystem.file_io import get_file_stat
from gyomu_schema.error.config import ConfigError
from pydantic import BaseModel
from returns.result import Failure, Success

from packages.schema.test_support.helpers import create_gyomu_io_error


class SomeConfig(BaseModel):
    name: str
    tags: list[str]


class TestFileCacheValidator:
    def test_get_state_returns_file_state_when_file_exists(self, mocker):
        path = Path("config.json")
        key = FileConfigCacheKey(path=path, config_type=SomeConfig)

        stat = Mock()
        stat.st_mtime_ns = 123456789
        stat.st_size = 256

        mocker.patch(
            "gyomu_config.cache.file.get_file_stat",
            return_value=Success(stat),
        )

        validator = FileCacheValidator()

        result = validator.get_state(key)

        assert result == Success(FileState(mtime_ns=123456789, size=256))

    def test_get_state_returns_none_when_file_does_not_exist(self, mocker):
        key = FileConfigCacheKey(path=Path("missing.json"), config_type=SomeConfig)

        mocker.patch(
            "gyomu_config.cache.file.get_file_stat",
            return_value=Success(None),
        )

        validator = FileCacheValidator()

        result = validator.get_state(key)

        assert result == Success(None)

    def test_get_state_returns_config_error_when_stat_fails(self, mocker):
        key = FileConfigCacheKey(path=Path("config.json"), config_type=SomeConfig)
        original_error = create_gyomu_io_error()

        mocker.patch(
            "gyomu_config.cache.file.get_file_stat",
            return_value=Failure(original_error),
        )

        validator = FileCacheValidator()

        result = validator.get_state(key)

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), ConfigError)

    def test_is_valid_returns_true_when_states_match(self):
        validator = FileCacheValidator()
        state = FileState(mtime_ns=123456789, size=256)

        assert validator.is_valid(state, state)

    def test_is_valid_returns_false_when_mtime_differs(self):
        validator = FileCacheValidator()

        cached_state = FileState(mtime_ns=100, size=256)
        current_state = FileState(mtime_ns=200, size=256)

        assert not validator.is_valid(cached_state, current_state)

    def test_is_valid_returns_false_when_size_differs(self):
        validator = FileCacheValidator()

        cached_state = FileState(mtime_ns=100, size=256)
        current_state = FileState(mtime_ns=100, size=512)

        assert not validator.is_valid(cached_state, current_state)


def write_config(path: Path, config: SomeConfig) -> None:
    path.write_text(
        config.model_dump_json(),
        encoding="utf-8",
    )


def make_key(path: Path) -> FileConfigCacheKey:
    return FileConfigCacheKey(path=path, config_type=SomeConfig)


class TestFileConfigCache:
    def test_get_returns_none_when_cache_is_empty(self, tmp_path: Path) -> None:
        path = tmp_path / "config.json"
        write_config(path, SomeConfig(name="example", tags=["one"]))

        cache = FileConfigCache[SomeConfig]()

        result = cache.get(make_key(path))

        assert result == Success(None)

    def test_get_returns_cached_value_when_file_is_unchanged(
        self,
        tmp_path: Path,
    ) -> None:
        path = tmp_path / "config.json"
        write_config(path, SomeConfig(name="example", tags=["one"]))

        cache = FileConfigCache[SomeConfig]()
        key = make_key(path)
        config = SomeConfig(name="example", tags=["one"])

        from gyomu_infra.filesystem.file_io import get_file_stat

        stat_result = get_file_stat(path)
        assert isinstance(stat_result, Success)
        stat = stat_result.unwrap()
        assert stat is not None

        from gyomu_config.cache.file import FileState

        cache._add(
            key,
            config,
            FileState(mtime_ns=stat.st_mtime_ns, size=stat.st_size),
        )

        result = cache.get(key)

        assert result == Success(config)

    def test_get_returns_none_when_file_is_modified(
        self,
        tmp_path: Path,
    ) -> None:
        path = tmp_path / "config.json"
        write_config(path, SomeConfig(name="before", tags=["one"]))

        cache = FileConfigCache[SomeConfig]()
        key = make_key(path)

        stat_result = get_file_stat(path)
        assert isinstance(stat_result, Success)
        stat = stat_result.unwrap()
        assert stat is not None

        cache._add(
            key,
            SomeConfig(name="before", tags=["one"]),
            FileState(mtime_ns=stat.st_mtime_ns, size=stat.st_size),
        )

        # サイズが確実に変わるように内容を更新する
        write_config(path, SomeConfig(name="after-modified", tags=["one", "two"]))

        result = cache.get(key)

        assert result == Success(None)

    def test_get_returns_none_when_file_is_deleted(
        self,
        tmp_path: Path,
    ) -> None:
        path = tmp_path / "config.json"
        write_config(path, SomeConfig(name="example", tags=["one"]))

        cache = FileConfigCache[SomeConfig]()
        key = make_key(path)

        stat_result = get_file_stat(path)
        assert isinstance(stat_result, Success)
        stat = stat_result.unwrap()
        assert stat is not None

        cache._add(
            key,
            SomeConfig(name="example", tags=["one"]),
            FileState(mtime_ns=stat.st_mtime_ns, size=stat.st_size),
        )

        path.unlink()

        result = cache.get(key)

        assert result == Success(None)
