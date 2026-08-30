from collections.abc import Callable
from dataclasses import dataclass

from gyomu_ai.execution.context import AiModelContext
from pydantic_ai import Embedder
from pydantic_ai.models import Model


@dataclass(frozen=True)
class PydanticAiModelRegistry:
    fast: Callable[[AiModelContext | None], Model]
    smart: Callable[[AiModelContext | None], Model]
    reasoning: Callable[[AiModelContext | None], Model]
    vision: Callable[[AiModelContext | None], Model]
    embedding: Callable[[AiModelContext | None], Embedder]
