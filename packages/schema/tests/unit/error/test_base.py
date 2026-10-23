from types import SimpleNamespace
from unittest.mock import patch

from gyomu_schema.error import BaseError
from gyomu_schema.error.base import caller_context
from gyomu_schema.error.database import DatabaseError
from gyomu_schema.error.gyomu import GyomuError
from returns.result import Failure


def test_base_error_is_exception() -> None:
    error = BaseError("something went wrong")

    assert isinstance(error, Exception)
    assert str(error) == "something went wrong"


def test_base_error_has_context() -> None:
    error = BaseError(
        "something went wrong",
        context="test.context",
    )

    assert error.context == "test.context"


def test_base_error_has_details() -> None:
    details = {
        "operation": "test",
        "value": 123,
    }

    error = BaseError(
        "something went wrong",
        details=details,
    )

    assert error.details == details


def test_base_error_context_and_details_are_optional() -> None:
    error = BaseError("something went wrong")

    assert error.context is None
    assert error.details is None


def _simulate_error_constructor() -> str:
    """Simulate calling caller_context from an error constructor."""
    return caller_context()


class TestCallerContext:
    def test_returns_callers_module_and_function(self) -> None:
        result = _simulate_error_constructor()

        assert result == f"{__name__}.test_returns_callers_module_and_function"

    def test_returns_unknown_when_currentframe_is_none(self) -> None:
        with patch(
            "gyomu_schema.error.base.inspect.currentframe",
            return_value=None,
        ):
            result = caller_context()

        assert result == "<unknown>"

    def test_returns_unknown_when_caller_frame_is_none(self) -> None:
        frame = SimpleNamespace(f_back=None)

        with patch(
            "gyomu_schema.error.base.inspect.currentframe",
            return_value=frame,
        ):
            result = caller_context()

        assert result == "<unknown>"

    def test_returns_unknown_when_callers_caller_frame_is_none(
        self,
    ) -> None:
        caller_frame = SimpleNamespace(f_back=None)
        frame = SimpleNamespace(f_back=caller_frame)

        with patch(
            "gyomu_schema.error.base.inspect.currentframe",
            return_value=frame,
        ):
            result = caller_context()

        assert result == "<unknown>"

    def test_skips_lambda_frame(self) -> None:
        result = (lambda: caller_context())()

        assert result == f"{__name__}.test_skips_lambda_frame"

    def test_skips_nested_lambda_frames(self) -> None:
        result = (lambda: (lambda: caller_context())())()

        assert result == f"{__name__}.test_skips_nested_lambda_frames"

    def test_skips_result_lambda_frame(self) -> None:
        fail = Failure(DatabaseError(message="test"))
        fail2 = fail.alt(
            lambda error: GyomuError(
                message="gyomu",
                domain="domain",
                operation="operation",
                reason="concurrent_modification",
            ).chain(error)
        )
        fail_error = fail.failure()
        fail2_error = fail2.failure()
        assert fail2_error.context == f"{__name__}.test_skips_result_lambda_frame"
        assert fail2_error.context == fail_error.context
