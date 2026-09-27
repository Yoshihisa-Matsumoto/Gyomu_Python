import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Self


@dataclass(frozen=True)
class ExecutionTimer:
    """Measures execution duration and completion timestamps."""

    started_at: datetime
    """The datetime when the timer was started."""

    _started_monotonic: float
    """The monotonic timestamp when the timer was started."""

    @classmethod
    def start(cls) -> Self:
        """Starts and returns a new execution timer instance.

        Returns:
            Self: A new instance of ExecutionTimer.
        """
        return cls(
            started_at=datetime.now(UTC),
            _started_monotonic=time.monotonic(),
        )

    def complete(self) -> tuple[datetime, timedelta]:
        """Completes the timer and calculates elapsed time.

        Returns:
            tuple[datetime, timedelta]: A tuple containing the completion datetime and
                elapsed timedelta.
        """
        completed_at = datetime.now(UTC)
        duration = timedelta(
            seconds=time.monotonic() - self._started_monotonic,
        )
        return completed_at, duration
