from gyomu_schema.error import BaseError


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
