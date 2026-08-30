from datetime import UTC, datetime, timedelta

import pytest
from gyomu_schema.utility import execution_timer
from gyomu_schema.utility.execution_timer import ExecutionTimer


class TestExecutionTimer:
    def test_start_creates_timer(self) -> None:
        before = datetime.now(UTC)

        timer = ExecutionTimer.start()

        after = datetime.now(UTC)

        assert before <= timer.started_at <= after

    def test_complete_returns_completed_at_and_duration(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        current_time = 100.0

        monkeypatch.setattr(
            execution_timer.time,
            "monotonic",
            lambda: current_time,
        )

        timer = ExecutionTimer.start()

        current_time += 1.5

        completed_at, duration = timer.complete()

        assert completed_at >= timer.started_at
        assert duration == timedelta(seconds=1.5)

    def test_duration_is_measured_using_elapsed_time(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monotonic_time = 100.0

        monkeypatch.setattr(
            execution_timer.time,
            "monotonic",
            lambda: monotonic_time,
        )
        timer = ExecutionTimer.start()

        monotonic_time = 102.25

        _, duration = timer.complete()

        assert duration == timedelta(seconds=2.25)

    def test_complete_does_not_modify_timer(self) -> None:
        timer = ExecutionTimer.start()
        started_at = timer.started_at

        timer.complete()

        assert timer.started_at == started_at
