from collections.abc import Callable
from dataclasses import dataclass

from pydantic_ai import Embedder
from pydantic_ai.models import Model

from gyomu_ai.execution.context import AiModelContext
from gyomu_ai.model.ai_model import BucketId


@dataclass(frozen=True)
class PydanticAiModelDefinition:
    """Defines a Pydantic AI model definition containing a model creation function
    and bucket ID.
    """

    create_model: Callable[[AiModelContext | None], Model]
    """Function to create the AI model."""

    bucket_id: BucketId
    """The bucket ID associated with the model."""


@dataclass(frozen=True)
class PydanticAiEmbedderDefinition:
    """Defines a Pydantic AI embedder definition containing an embedder creation
    function and bucket ID.
    """

    create_embedder: Callable[[AiModelContext | None], Embedder]
    """Function to create the embedder."""

    bucket_id: BucketId
    """The bucket ID associated with the embedder."""


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
