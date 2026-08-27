import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Self


@dataclass(frozen=True)
class ExecutionTimer:
    started_at: datetime
    _started_monotonic: float

    @classmethod
    def start(cls) -> Self:
        return cls(
            started_at=datetime.now(UTC),
            _started_monotonic=time.monotonic(),
        )

    def complete(self) -> tuple[datetime, timedelta]:
        completed_at = datetime.now(UTC)
        duration = timedelta(
            seconds=time.monotonic() - self._started_monotonic,
        )
        return completed_at, duration
