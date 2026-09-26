from collections.abc import Callable
from dataclasses import dataclass

from pydantic_ai import Embedder
from pydantic_ai.models import Model

from gyomu_ai.execution.context import AiModelContext


@dataclass(frozen=True)
class PydanticAiModelRegistry:
    """Registry for Pydantic AI models across various capabilities."""

    fast: Callable[[AiModelContext | None], Model]
    """Callable returning a fast model."""

    smart: Callable[[AiModelContext | None], Model]
    """Callable returning a smart model."""

    reasoning: Callable[[AiModelContext | None], Model]
    """Callable returning a reasoning model."""

    vision: Callable[[AiModelContext | None], Model]
    """Callable returning a vision model."""

    embedding: Callable[[AiModelContext | None], Embedder]
    """Callable returning an embedder."""
