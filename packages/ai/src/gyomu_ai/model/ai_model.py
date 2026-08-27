from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from gyomu_ai.execution.context import AiModelContext


class AiModelKey(StrEnum):
    FAST = "fast"
    SMART = "smart"
    REASONING = "reasoning"
    VISION = "vision"
    EMBEDDING = "embedding"


@dataclass(frozen=True)
class AiModelRegistry[TLanguageModel, TEmbeddingModel]:
    fast: Callable[[AiModelContext], TLanguageModel]
    smart: Callable[[AiModelContext], TLanguageModel]
    reasoning: Callable[[AiModelContext], TLanguageModel]
    vision: Callable[[AiModelContext], TLanguageModel]
    embedding: Callable[[AiModelContext], TEmbeddingModel]
