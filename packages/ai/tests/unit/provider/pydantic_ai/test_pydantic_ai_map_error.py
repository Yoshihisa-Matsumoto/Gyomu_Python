from typing import Any

from gyomu_ai.provider.pydantic_ai.map_error import map_pydantic_ai_error
from gyomu_schema.error.ai import (
    AiError,
    AiErrorPhase,
    AiOperation,
    AiRetryAfter,
    AiRetryExponential,
    AiRetryResolution,
)
from pydantic_ai.exceptions import ModelHTTPError


class TestMapPydanticAiError:
    @staticmethod
    def _create_http_error(
        status_code: int,
        body: dict[str, Any],
        model_name: str = "gemini-3.5-flash-lite",
    ) -> ModelHTTPError:
        return ModelHTTPError(
            status_code=status_code,
            model_name=model_name,
            body=body,
        )

    def test_maps_rate_limit_with_retry_info(self) -> None:
        error = self._create_http_error(
            429,
            {
                "error": {
                    "code": 429,
                    "message": "quota exceeded",
                    "status": "RESOURCE_EXHAUSTED",
                    "details": [
                        {
                            "@type": "type.googleapis.com/google.rpc.RetryInfo",
                            "retryDelay": "31s",
                        },
                    ],
                },
            },
        )

        result = map_pydantic_ai_error(
            error,
            operation=AiOperation.GENERATE,
            model_key="google-gemini",
            model="fast",
        )

        assert isinstance(result, AiError)
        assert result.operation == AiOperation.GENERATE
        assert result.model_key == "google-gemini"
        assert result.model == "gemini-3.5-flash-lite"
        assert result.phase == AiErrorPhase.RATE_LIMIT
        assert result.status_code == 429

        assert isinstance(result.resolution, AiRetryResolution)
        assert isinstance(result.resolution.strategy, AiRetryAfter)
        assert result.resolution.strategy.delay_second == 31.0

    def test_maps_rate_limit_without_retry_info_to_exponential(self) -> None:
        error = self._create_http_error(
            429,
            {
                "error": {
                    "code": 429,
                    "message": "quota exceeded",
                },
            },
        )

        result = map_pydantic_ai_error(
            error,
            operation=AiOperation.GENERATE,
            model_key="google-gemini",
            model="fast",
        )

        assert result.phase == AiErrorPhase.RATE_LIMIT
        assert result.status_code == 429
        assert isinstance(result.resolution, AiRetryResolution)
        assert isinstance(result.resolution.strategy, AiRetryExponential)

    def test_maps_server_error_to_exponential_retry(self) -> None:
        error = self._create_http_error(
            503,
            {
                "error": {
                    "code": 503,
                    "message": "service unavailable",
                },
            },
        )

        result = map_pydantic_ai_error(
            error,
            operation=AiOperation.GENERATE,
            model_key="google-gemini",
            model="fast",
        )

        assert result.phase == AiErrorPhase.RESPONSE
        assert result.status_code == 503
        assert isinstance(result.resolution, AiRetryResolution)
        assert isinstance(result.resolution.strategy, AiRetryExponential)

    def test_maps_bad_request_to_fail(self) -> None:
        error = self._create_http_error(
            400,
            {
                "error": {
                    "code": 400,
                    "message": "invalid request",
                },
            },
        )

        result = map_pydantic_ai_error(
            error,
            operation=AiOperation.GENERATE,
            model_key="google-gemini",
            model="fast",
        )

        assert result.phase == AiErrorPhase.REQUEST
        assert result.status_code == 400
        assert result.resolution.__class__.__name__ == "AiFailResolution"

    def test_maps_unknown_error_to_fail(self) -> None:
        error = RuntimeError("something went wrong")

        result = map_pydantic_ai_error(
            error,
            operation=AiOperation.GENERATE,
            model_key="google-gemini",
            model="fast",
        )

        assert result.operation == AiOperation.GENERATE
        assert result.model_key == "google-gemini"
        assert result.model == "fast"
        assert result.phase == AiErrorPhase.REQUEST
        assert result.status_code is None
        assert result.resolution.__class__.__name__ == "AiFailResolution"
