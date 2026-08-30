from gyomu_schema.error.ai import (
    AiError,
    AiErrorPhase,
    AiFailResolution,
    AiFallbackResolution,
    AiOperation,
    AiRetryAfter,
    AiRetryExponential,
    AiRetryImmediate,
    AiRetryResolution,
)


class TestAiError:
    def test_initializes_with_all_fields(self) -> None:
        resolution = AiRetryResolution(
            strategy=AiRetryAfter(delay_second=2.5),
        )

        error = AiError(
            "AI request failed",
            operation=AiOperation.GENERATE,
            model_key="fast",
            model="gemini-2.5-pro",
            phase=AiErrorPhase.RATE_LIMIT,
            resolution=resolution,
            status_code=429,
            context="pydantic-ai.generate",
            details={
                "quota_id": "GenerateRequestsPerMinute",
            },
        )

        assert str(error) == "AI request failed"

        assert error.operation is AiOperation.GENERATE
        assert error.model_key == "fast"
        assert error.model == "gemini-2.5-pro"
        assert error.phase is AiErrorPhase.RATE_LIMIT
        assert error.resolution is resolution
        assert error.status_code == 429

        assert error.context == "pydantic-ai.generate"
        assert error.details == {
            "quota_id": "GenerateRequestsPerMinute",
        }

    def test_allows_optional_fields_to_be_none(self) -> None:
        error = AiError(
            "AI request failed",
            operation=AiOperation.GENERATE,
            model_key=None,
            model=None,
            phase=AiErrorPhase.REQUEST,
            resolution=AiFailResolution(),
        )

        assert error.model_key is None
        assert error.model is None
        assert error.status_code is None
        assert error.context is None
        assert error.details is None

    def test_preserves_cause(self) -> None:
        cause = ValueError("original error")

        error = AiError(
            "AI request failed",
            operation=AiOperation.GENERATE,
            model_key="fast",
            model=None,
            phase=AiErrorPhase.REQUEST,
            resolution=AiFailResolution(),
        ).chain(cause)

        assert error.__cause__ is cause

    def test_supports_retry_immediate(self) -> None:
        resolution = AiRetryResolution(
            strategy=AiRetryImmediate(),
        )

        error = AiError(
            "AI request failed",
            operation=AiOperation.GENERATE,
            model_key="fast",
            model=None,
            phase=AiErrorPhase.REQUEST,
            resolution=resolution,
        )

        assert error.resolution is resolution
        assert isinstance(error.resolution, AiRetryResolution)
        assert isinstance(error.resolution.strategy, AiRetryImmediate)

    def test_supports_retry_exponential(self) -> None:
        resolution = AiRetryResolution(
            strategy=AiRetryExponential(),
        )

        error = AiError(
            "AI request failed",
            operation=AiOperation.GENERATE,
            model_key="smart",
            model="gemini-2.5-pro",
            phase=AiErrorPhase.RESPONSE,
            resolution=resolution,
            status_code=503,
        )

        assert error.resolution is resolution
        assert isinstance(error.resolution, AiRetryResolution)
        assert isinstance(error.resolution.strategy, AiRetryExponential)

    def test_supports_retry_after(self) -> None:
        resolution = AiRetryResolution(
            strategy=AiRetryAfter(delay_second=1.5),
        )

        error = AiError(
            "AI request failed",
            operation=AiOperation.GENERATE,
            model_key="fast",
            model=None,
            phase=AiErrorPhase.RATE_LIMIT,
            resolution=resolution,
            status_code=429,
        )

        assert error.resolution is resolution

        assert isinstance(error.resolution, AiRetryResolution)
        strategy = error.resolution.strategy
        assert isinstance(strategy, AiRetryAfter)
        assert strategy.delay_second == 1.5

    def test_supports_fallback_and_fail_resolutions(self) -> None:
        fallback_error = AiError(
            "AI request failed",
            operation=AiOperation.GENERATE,
            model_key="fast",
            model=None,
            phase=AiErrorPhase.RATE_LIMIT,
            resolution=AiFallbackResolution(),
        )

        fail_error = AiError(
            "AI request failed",
            operation=AiOperation.GENERATE,
            model_key="fast",
            model=None,
            phase=AiErrorPhase.REQUEST,
            resolution=AiFailResolution(),
        )

        assert isinstance(fallback_error.resolution, AiFallbackResolution)
        assert isinstance(fail_error.resolution, AiFailResolution)
