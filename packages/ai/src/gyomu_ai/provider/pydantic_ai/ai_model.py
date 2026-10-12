from collections.abc import Callable
from dataclasses import dataclass

from pydantic_ai import Embedder
from pydantic_ai.models import Model

from gyomu_ai.execution.context import AiModelContext
from gyomu_ai.model.ai_model import BucketId


@dataclass(frozen=True)
class PydanticAiModelDefinition:
    create_model: Callable[[AiModelContext | None], Model]
    bucket_id: BucketId


@dataclass(frozen=True)
class PydanticAiEmbedderDefinition:
    create_embedder: Callable[[AiModelContext | None], Embedder]
    bucket_id: BucketId


@dataclass(frozen=True)
class PydanticAiModelRegistry:
    """Registry for Pydantic AI models across various capabilities."""

    fast: PydanticAiModelDefinition
    """Callable returning a fast model."""

    smart: PydanticAiModelDefinition
    """Callable returning a smart model."""

    reasoning: PydanticAiModelDefinition
    """Callable returning a reasoning model."""

    vision: PydanticAiModelDefinition
    """Callable returning a vision model."""

    embedding: PydanticAiEmbedderDefinition
    """Callable returning an embedder."""
