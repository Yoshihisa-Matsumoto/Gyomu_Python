from collections.abc import Hashable
from dataclasses import dataclass
from typing import Protocol

from gyomu_schema.error.config import ConfigError
from pydantic import BaseModel
from returns.result import Failure, Result, Success


@dataclass(frozen=True)
class CacheEntry[T, S]:
    value: T
    state: S


class CacheValidator[K: Hashable, S](Protocol):
    def get_state(self, key: K) -> Result[S | None, ConfigError]: ...

    def is_valid(self, cached_state: S, current_state: S) -> bool: ...


class _ConfigCache[
    T: BaseModel,
    K: Hashable,
    S,
]:
    _cache: dict[K, CacheEntry[T, S]]
    _validator: CacheValidator[K, S]

    def __init__(self, validator: CacheValidator[K, S]) -> None:
        self._cache = {}
        self._validator = validator

    def add_with_current_state(
        self,
        key: K,
        value: T,
    ) -> Result[None, ConfigError]:
        state_result = self._validator.get_state(key)
        if isinstance(state_result, Failure):
            return state_result

        state = state_result.unwrap()
        if state is None:
            return Success(None)

        self._add(key, value, state)
        return Success(None)

    def _add(self, key: K, value: T, state: S) -> None:
        self._cache[key] = CacheEntry(
            value=value.model_copy(deep=True),
            state=state,
        )

    def get(
        self,
        key: K,
    ) -> Result[T | None, ConfigError]:
        state_result = self._validator.get_state(key)
        if isinstance(state_result, Failure):
            return state_result
        state = state_result.unwrap()
        if state is None:
            self._cache.pop(key, None)
            return Success(None)
        entry = self._cache.get(key)

        if entry is not None and self._validator.is_valid(entry.state, state):
            return Success(entry.value.model_copy(deep=True))

        self._cache.pop(key, None)
        return Success(None)
