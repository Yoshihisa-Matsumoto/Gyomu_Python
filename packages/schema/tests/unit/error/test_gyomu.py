from gyomu_schema.error import GyomuError


def test_gyomu_error_has_application_context() -> None:
    error = GyomuError(
        "fetch holiday failed",
        operation="fetch_holiday",
        domain="market",
        reason="external_failure",
    )

    assert str(error) == "fetch holiday failed"
    assert error.operation == "fetch_holiday"
    assert error.domain == "market"
    assert error.reason == "external_failure"
    assert error.retryable is False

def test_gyomu_error_can_be_retryable() -> None:
    error = GyomuError(
        "request failed",
        operation="fetch_holiday",
        domain="market",
        reason="external_failure",
        retryable=True,
    )

    assert error.retryable is True

def test_gyomu_error_has_base_error_context() -> None:
    error = GyomuError(
        "fetch holiday failed",
        operation="fetch_holiday",
        domain="market",
        reason="external_failure",
        context="MarketHolidayService.fetch_holiday",
        details={
            "market": "JPX",
        },
    )

    assert error.context == "MarketHolidayService.fetch_holiday"
    assert error.details == {
        "market": "JPX",
    }
