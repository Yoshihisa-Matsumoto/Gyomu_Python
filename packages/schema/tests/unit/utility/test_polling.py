from unittest.mock import MagicMock

from gyomu_schema.error.timeout import GyomuTimeoutError
from gyomu_schema.utility.polling import polling
from returns.result import Failure, Success


class FakeClock:
    def __init__(self) -> None:
        self.current_time = 0.0

    def now(self) -> float:
        return self.current_time

    def advance(self, seconds: float) -> None:
        self.current_time += seconds


class TestPolling:
    def test_succeeds_immediately(self) -> None:
        action = MagicMock(return_value=True)
        clock = FakeClock()
        sleep = MagicMock()

        result = polling(
            action_name="test action",
            timeout_seconds=10,
            interval_seconds=1,
            action=action,
            clock=clock.now,
            sleep=sleep,
        )

        assert result == Success(True)
        assert action.call_count == 1
        sleep.assert_not_called()

    def test_succeeds_after_multiple_attempts(self) -> None:
        action = MagicMock(side_effect=[False, False, True])
        clock = FakeClock()

        def sleep(seconds: float) -> None:
            clock.advance(seconds)

        result = polling(
            action_name="test action",
            timeout_seconds=10,
            interval_seconds=2,
            action=action,
            clock=clock.now,
            sleep=sleep,
        )

        assert result == Success(True)
        assert action.call_count == 3
        assert clock.current_time == 4.0

    def test_returns_failure_on_timeout(self) -> None:
        action = MagicMock(return_value=False)
        clock = FakeClock()

        def sleep(seconds: float) -> None:
            clock.advance(seconds)

        result = polling(
            action_name="test action",
            timeout_seconds=5,
            interval_seconds=2,
            action=action,
            clock=clock.now,
            sleep=sleep,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuTimeoutError)
        assert action.call_count == 4
        assert clock.current_time == 6.0

        error = result.failure()

        assert error.action == "test action"
        assert error.timeout_seconds == 5
        assert error.interval_seconds == 2
