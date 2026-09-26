from collections.abc import Mapping
from dataclasses import dataclass

from gyomu_schema.option.retry import RetryOption


@dataclass(frozen=True)
class AiModelContext:
    """Represents execution context for AI models containing request headers."""

    headers: Mapping[str, str] | None = None
    """Optional HTTP headers to include with AI model requests."""


@dataclass(frozen=True)
class AiExecutionContext(AiModelContext):
    """Represents extended execution context for AI model calls including generation
    and retry options.
    """

    temperature: float | None = None
    """Optional sampling temperature for response generation."""

    retry_option: RetryOption | None = None
    """Optional retry configuration for handling execution failures."""

    max_tokens: int | None = None
    """Optional maximum number of tokens to generate in the response."""
