from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation


class TestGyomuIOError:
    def test_initializes_with_required_fields(self) -> None:
        error = GyomuIOError(
            "Failed to read file.",
            layer=IOLayer.FILESYSTEM,
            operation=IOOperation.READ,
        )

        assert error.message == "Failed to read file."
        assert error.layer == IOLayer.FILESYSTEM
        assert error.operation == IOOperation.READ
        assert error.target is None
        assert error.retryable is False
        assert error.reason is None

    def test_initializes_with_optional_fields(self) -> None:
        error = GyomuIOError(
            "Failed to read file.",
            layer=IOLayer.FILESYSTEM,
            operation=IOOperation.READ,
            target="/tmp/example.txt",
            retryable=True,
            reason="Permission denied.",
            context="Loading configuration.",
            details={"exception_type": "PermissionError"},
        )

        assert error.message == "Failed to read file."
        assert error.layer == IOLayer.FILESYSTEM
        assert error.operation == IOOperation.READ
        assert error.target == "/tmp/example.txt"
        assert error.retryable is True
        assert error.reason == "Permission denied."
        assert error.context == "Loading configuration."
        assert error.details == {
            "exception_type": "PermissionError",
        }

    def test_supports_all_io_layers(self) -> None:
        for layer in IOLayer:
            error = GyomuIOError(
                "I/O error.",
                layer=layer,
                operation=IOOperation.READ,
            )

            assert error.layer == layer

    def test_supports_all_io_operations(self) -> None:
        for operation in IOOperation:
            error = GyomuIOError(
                "I/O error.",
                layer=IOLayer.FILESYSTEM,
                operation=operation,
            )

            assert error.operation == operation

    def test_retryable_defaults_to_false(self) -> None:
        error = GyomuIOError(
            "I/O error.",
            layer=IOLayer.FILESYSTEM,
            operation=IOOperation.READ,
        )

        assert error.retryable is False

    def test_retryable_can_be_true(self) -> None:
        error = GyomuIOError(
            "Temporary I/O error.",
            layer=IOLayer.STREAM,
            operation=IOOperation.READ,
            retryable=True,
        )

        assert error.retryable is True
