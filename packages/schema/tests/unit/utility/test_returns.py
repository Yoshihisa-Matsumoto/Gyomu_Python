from gyomu_schema.utility.returns import from_async, from_sync
from returns.result import Failure, Success


class TestFromSync:
    def test_returns_success_when_function_succeeds(self) -> None:
        result = from_sync(
            lambda: 42,
            build_error=lambda e: RuntimeError(str(e)),
        )

        assert isinstance(result, Success)
        assert result.unwrap() == 42

    def test_returns_failure_with_built_error_when_function_raises(
        self,
    ) -> None:
        original_error = ValueError("test error")
        expected_error = RuntimeError("wrapped error")

        def f() -> int:
            raise original_error

        def build_error(error: Exception) -> RuntimeError:
            assert error is original_error
            return expected_error

        result = from_sync(
            f,
            build_error=build_error,
        )

        assert isinstance(result, Failure)
        assert result.failure() is expected_error

    def test_build_error_can_convert_to_custom_error_type(self) -> None:
        class CustomError(Exception):
            pass

        result = from_sync(
            lambda: (_ for _ in ()).throw(ValueError("original")),
            build_error=lambda e: CustomError(f"converted: {e}"),
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), CustomError)
        assert str(result.failure()) == "converted: original"


class TestFromAsync:
    async def test_returns_success_when_function_succeeds(self) -> None:
        async def f() -> int:
            return 42

        result = await from_async(
            f,
            build_error=lambda e: RuntimeError(str(e)),
        )

        assert isinstance(result, Success)
        assert result.unwrap() == 42

    async def test_returns_failure_with_built_error_when_function_raises(
        self,
    ) -> None:
        original_error = ValueError("test error")
        expected_error = RuntimeError("wrapped error")

        async def f() -> int:
            raise original_error

        def build_error(error: Exception) -> RuntimeError:
            assert error is original_error
            return expected_error

        result = await from_async(
            f,
            build_error=build_error,
        )

        assert isinstance(result, Failure)
        assert result.failure() is expected_error

    async def test_build_error_can_convert_to_custom_error_type(self) -> None:
        class CustomError(Exception):
            pass

        async def f() -> int:
            raise ValueError("original")

        result = await from_async(
            f,
            build_error=lambda e: CustomError(f"converted: {e}"),
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), CustomError)
        assert str(result.failure()) == "converted: original"
