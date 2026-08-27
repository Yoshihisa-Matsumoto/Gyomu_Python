from collections.abc import Callable
from dataclasses import dataclass

from gyomu_ai.execution.context import AiModelContext
from pydantic_ai import Agent, Embedder


@dataclass(frozen=True)
class PydanticAiModelRegistry:
    fast: Callable[[AiModelContext], Agent]
    smart: Callable[[AiModelContext], Agent]
    reasoning: Callable[[AiModelContext], Agent]
    vision: Callable[[AiModelContext], Agent]
    embedding: Callable[[AiModelContext], Embedder]
