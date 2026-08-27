from collections.abc import Callable
from dataclasses import dataclass

from gyomu_schema.error.ai import AiError


@dataclass(frozen=True)
class RetryParameter:
    error: AiError
    attempt: int
    delay_milliseconds: int


class RetryObserver:
    on_retry: Callable[[RetryParameter], None]


@dataclass(frozen=True)
class RetryOption:
    max_attempts: int | None

    observer: RetryObserver | None
