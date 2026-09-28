# result.py
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Result(Generic[T]):
    value: T | None
    error: str | None

    @classmethod
    def success(cls, value: T) -> "Result[T]":
        return cls(value=value, error=None)

    @classmethod
    def failure(cls, error: str) -> "Result[T]":
        return cls(value=None, error=error)
