from dataclasses import dataclass
from enum import StrEnum

from pydantic import BaseModel

from gyomu_ai.execution.context import AiExecutionContext
from gyomu_ai.model.ai_model import AiModelKey


@dataclass(frozen=True)
class GenerateTextParams:
    key: AiModelKey
    execution: AiExecutionContext | None = None
    tool: ToolConfig | None = None


@dataclass(frozen=True)
class StreamTextParams:
    key: AiModelKey
    execution: AiExecutionContext | None = None
    tool: ToolConfig | None = None


@dataclass(frozen=True)
class GenerateObjectParams[T: BaseModel]:
    key: AiModelKey
    output_type: type[T]
    execution: AiExecutionContext | None = None
    tool: ToolConfig | None = None


class AiEmbeddingMode(StrEnum):
    QUERY = "query"
    DOCUMENT = "document"


@dataclass(frozen=True)
class EmbedParams[T]:
    execution: AiExecutionContext
    value: T
    mode: AiEmbeddingMode


@dataclass(frozen=True)
class ToolLoopPolicyMaxSteps:
    max_steps: int


@dataclass(frozen=True)
class ToolLoopPolicyUntilToolCalled:
    tool_name: str


@dataclass(frozen=True)
class ToolLoopPolicyUntilFinished:
    pass


type ToolLoopPolicy = (
    ToolLoopPolicyMaxSteps | ToolLoopPolicyUntilToolCalled | ToolLoopPolicyUntilFinished
)


@dataclass(frozen=True)
class ToolConfig:
    tool_loop_policy: ToolLoopPolicy
