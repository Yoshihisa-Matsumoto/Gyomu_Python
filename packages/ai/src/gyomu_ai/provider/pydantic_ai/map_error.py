import re
from collections.abc import Mapping
from typing import Any

from gyomu_infra.logger import logger
from gyomu_schema.error.ai import (
    AiError,
    AiErrorPhase,
    AiErrorResolution,
    AiFailResolution,
    AiOperation,
    AiRetryAfter,
    AiRetryExponential,
    AiRetryResolution,
)
from pydantic_ai.exceptions import ModelHTTPError


def map_pydantic_ai_error(
    error: BaseException,
    *,
    operation: AiOperation,
    model_key: str | None,
    model: str | None,
) -> AiError:
    """Map a Pydantic AI exception to a standardized AI error.

    Returns:
        AiError: Standardized AI error object
    """
    if isinstance(error, ModelHTTPError):
        return _map_model_http_error(
            error,
            operation=operation,
            model_key=model_key,
        )

    return AiError(
        str(error),
        operation=operation,
        model_key=model_key,
        model=model,
        phase=AiErrorPhase.REQUEST,
        resolution=AiFailResolution(),
    )


def _map_model_http_error(
    error: ModelHTTPError,
    *,
    operation: AiOperation,
    model_key: str | None,
) -> AiError:
    """Map a model HTTP error to a standardized AI error.

    Returns:
        AiError: Standardized AI error object
    """
    status_code = error.status_code
    model = error.model_name

    if status_code == 429:
        return _map_rate_limit_error(
            error,
            operation=operation,
            model_key=model_key,
            model=model,
        )

    if status_code >= 500:
        resolution: AiErrorResolution = AiRetryResolution(
            strategy=AiRetryExponential(),
        )
        phase = AiErrorPhase.RESPONSE
        logger.info(f"AI LLM error: status={status_code}")
    else:
        resolution = AiFailResolution()
        phase = AiErrorPhase.REQUEST

    return AiError(
        str(error),
        operation=operation,
        model_key=model_key,
        model=model,
        phase=phase,
        resolution=resolution,
        status_code=status_code,
    )


def _map_rate_limit_error(
    error: ModelHTTPError,
    *,
    operation: AiOperation,
    model_key: str | None,
    model: str | None,
) -> AiError:
    """Map a rate limit error to a standardized AI error with retry resolution.

    Returns:
        AiError: Standardized AI error object
    """
    delay_second = _extract_retry_delay(error)

    if delay_second is not None:
        resolution: AiErrorResolution = AiRetryResolution(
            strategy=AiRetryAfter(delay_second=delay_second + 1),
        )
        logger.debug(f"Rate Limit: {delay_second} second")
    else:
        resolution = AiRetryResolution(
            strategy=AiRetryExponential(),
        )
        logger.debug("Rate Limit exponential")

    return AiError(
        str(error),
        operation=operation,
        model_key=model_key,
        model=model,
        phase=AiErrorPhase.RATE_LIMIT,
        resolution=resolution,
        status_code=429,
    )


def _extract_retry_delay(error: ModelHTTPError) -> float | None:
    """Extract the retry delay from a model HTTP error.

    Returns:
        float | None: Retry delay in seconds, or None if not found
    """
    retry_after = error.retry_after
    if retry_after is not None:
        return retry_after

    body = error.body
    if not isinstance(body, Mapping):
        return None
    return _extract_retry_delay_from_body(body)


def _extract_retry_delay_from_body(
    body: Mapping[str, Any],
) -> float | None:
    """Extract the retry delay from an error response body.

    Returns:
        float | None: Retry delay in seconds, or None if not found
    """
    error_body = body.get("error")
    if not isinstance(error_body, Mapping):
        return None

    details = error_body.get("details")
    if not isinstance(details, list):
        return None

    for detail in details:
        if not isinstance(detail, Mapping):
            continue

        retry_delay = detail.get("retryDelay")
        if not isinstance(retry_delay, str):
            continue

        match = re.fullmatch(r"(\d+(?:\.\d+)?)s", retry_delay.strip())
        if match is None:
            continue

        return float(match.group(1))

    return None
