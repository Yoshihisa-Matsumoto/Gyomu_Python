from collections.abc import Callable
from dataclasses import dataclass

from gyomu_schema.error.ai import AiError


@dataclass(frozen=True)
class RetryParameter:
    """Represents the parameters associated with a retry attempt."""

    error: AiError
    """The AI error that triggered the retry."""

    attempt: int
    """The current attempt number."""

    delay_milliseconds: int
    """The delay in milliseconds before the next attempt."""


class RetryObserver:
    """Observer interface or container for handling retry events."""

    on_retry: Callable[[RetryParameter], None]
    """Callback function invoked on each retry attempt."""


@dataclass(frozen=True)
class RetryOption:
    """Defines configuration options for retry behavior."""

    max_attempts: int | None
    """The maximum number of retry attempts allowed."""

    observer: RetryObserver | None
    """The retry observer instance for tracking retry events."""
