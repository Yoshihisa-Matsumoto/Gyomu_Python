from dataclasses import dataclass
from unittest.mock import Mock

import pytest
from gyomu_config.cache.base import _ConfigCache
from gyomu_schema.error.config import ConfigError
from pydantic import BaseModel
from returns.result import Failure, Success


class TestConfig(BaseModel):
    name: str
    tags: list[str]


class TestKey(BaseModel):
    # キーは Hashable が必要なので、実際のテストでは
    # frozen dataclass などを使う。
    pass


@dataclass(frozen=True)
class CacheKey:
    name: str


@dataclass(frozen=True)
class CacheState:
    version: int


@pytest.fixture
def validator():
    return Mock()


@pytest.fixture
def cache(validator) -> _ConfigCache[TestConfig, CacheKey, CacheState]:
    return _ConfigCache[TestConfig, CacheKey, CacheState](validator)


@pytest.fixture
def key() -> CacheKey:
    return CacheKey(name="test")


@pytest.fixture
def state() -> CacheState:
    return CacheState(version=1)


@pytest.fixture
def config() -> TestConfig:
    return TestConfig(name="example", tags=["one", "two"])


class TestConfigCache:
    def test_add_and_get(
        self,
        cache: _ConfigCache[TestConfig, CacheKey, CacheState],
        validator,
        key,
        state,
        config,
    ):
        validator.get_state.return_value = Success(state)
        validator.is_valid.return_value = True

        cache._add(key, config, state)

        result = cache.get(key)

        assert result == Success(config)
        validator.get_state.assert_called_once_with(key)
        validator.is_valid.assert_called_once_with(state, state)

    def test_add_copies_value(
        self,
        cache: _ConfigCache[TestConfig, CacheKey, CacheState],
        validator,
        key,
        state,
        config,
    ):
        validator.get_state.return_value = Success(state)
        validator.is_valid.return_value = True

        cache._add(key, config, state)
        config.tags.append("modified")

        result = cache.get(key)

        assert result == Success(TestConfig(name="example", tags=["one", "two"]))

    def test_get_returns_copy(
        self,
        cache: _ConfigCache[TestConfig, CacheKey, CacheState],
        validator,
        key,
        state,
        config,
    ):
        validator.get_state.return_value = Success(state)
        validator.is_valid.return_value = True

        cache._add(key, config, state)

        first_result = cache.get(key)
        assert isinstance(first_result, Success)
        first_value = first_result.unwrap()
        assert first_value is not None

        first_value.tags.append("modified")

        second_result = cache.get(key)

        assert second_result == Success(TestConfig(name="example", tags=["one", "two"]))

    def test_get_returns_none_on_cache_miss(
        self,
        cache: _ConfigCache[TestConfig, CacheKey, CacheState],
        validator,
        key,
        state,
    ):
        validator.get_state.return_value = Success(state)

        result = cache.get(key)

        assert result == Success(None)
        validator.is_valid.assert_not_called()

    def test_get_returns_none_when_state_differs(
        self,
        cache: _ConfigCache[TestConfig, CacheKey, CacheState],
        validator,
        key,
        state,
        config,
    ):
        current_state = CacheState(version=2)
        validator.get_state.return_value = Success(current_state)
        validator.is_valid.return_value = False

        cache._add(key, config, state)

        result = cache.get(key)

        assert result == Success(None)
        validator.is_valid.assert_called_once_with(state, current_state)

    def test_get_propagates_state_error(
        self, cache: _ConfigCache[TestConfig, CacheKey, CacheState], validator, key
    ):
        error = ConfigError(
            message="fail to get file state",
            phase="load",
            source="json",
        )
        validator.get_state.return_value = Failure(error)

        result = cache.get(key)

        assert result == Failure(error)

    def test_get_removes_entry_when_state_is_none(
        self,
        cache: _ConfigCache[TestConfig, CacheKey, CacheState],
        validator,
        key,
        state,
        config,
    ):
        cache._add(key, config, state)
        validator.get_state.return_value = Success(None)

        result = cache.get(key)

        assert result == Success(None)
        assert key not in cache._cache

    def test_add_with_current_state(
        self,
        cache: _ConfigCache[TestConfig, CacheKey, CacheState],
        validator,
        key,
        state,
        config,
    ):
        validator.get_state.return_value = Success(state)

        result = cache.add_with_current_state(key, config)

        assert result == Success(None)
        validator.get_state.assert_called_once_with(key)

        # 登録された値を取得できることも確認
        validator.get_state.return_value = Success(state)
        validator.is_valid.return_value = True

        cached_result = cache.get(key)

        assert cached_result == Success(config)
        validator.is_valid.assert_called_once_with(state, state)

    def test_add_with_current_state_propagates_state_error(
        self,
        cache: _ConfigCache[TestConfig, CacheKey, CacheState],
        validator,
        key,
        config,
    ):
        error = ConfigError(
            message="fail to get file state",
            phase="load",
            source="json",
        )
        validator.get_state.return_value = Failure(error)

        result = cache.add_with_current_state(key, config)

        assert result == Failure(error)
        assert key not in cache._cache

    def test_add_with_current_state_does_not_add_when_state_is_none(
        self,
        cache: _ConfigCache[TestConfig, CacheKey, CacheState],
        validator,
        key,
        config,
    ):
        validator.get_state.return_value = Success(None)

        result = cache.add_with_current_state(key, config)

        assert result == Success(None)
        assert key not in cache._cache
        validator.get_state.assert_called_once_with(key)
