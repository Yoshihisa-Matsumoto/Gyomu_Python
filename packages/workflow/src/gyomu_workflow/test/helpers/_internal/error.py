from gyomu_schema.error.gyomu import GyomuError, GyomuErrorReason


def wrap_gyomu_error(
    error: BaseException, message: str, reason: GyomuErrorReason = "external_failure"
) -> GyomuError:
    return GyomuError(
        message=message,
        domain="Test Workflow",
        operation="Helper Inventories",
        reason=reason,
    ).chain(error)
