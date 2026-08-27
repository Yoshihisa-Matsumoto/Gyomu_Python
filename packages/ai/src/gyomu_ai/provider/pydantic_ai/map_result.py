from gyomu_ai.execution.result import (
    AiAssistantMessage,
    AiEmbeddingResult,
    AiFinishReason,
    AiGenerateObjectResult,
    AiGenerateTextResult,
    AiGenerationMetadata,
    AiUsage,
)
from gyomu_schema.utility.execution_timer import ExecutionTimer
from pydantic import BaseModel
from pydantic_ai import (
    AgentRunResult,
    EmbeddingResult,
    FinishReason,
    ModelResponseState,
)


def map_pydantic_finish_reason(
    reason: FinishReason | None, state: ModelResponseState
) -> AiFinishReason | None:
    if reason is None:
        return None
    match reason:
        case "content_filter":
            return "content-filtered"
        case "error":
            return "error"
        case "length":
            return "max-tokens"
        case "stop":
            # if state == "complete":
            #     return "completed"
            # elif state == "interrupted":
            #     return "cancelled"
            # elif state == "incomplete":
            #     return "error"
            # else:
            #     return "error"
            match state:
                case "complete":
                    return "completed"
                case "interrupted":
                    return "cancelled"
                case _:
                    return "error"
        case "tool_call":
            return "tool-call"


def _map_result_metadata[T](
    timer: ExecutionTimer, response: AgentRunResult[T] | EmbeddingResult
) -> AiGenerationMetadata:
    complete_result = timer.complete()
    if isinstance(response, EmbeddingResult):
        return AiGenerationMetadata(
            started_at=timer.started_at,
            completed_at=complete_result[0],
            elapsed_second=complete_result[1].total_seconds(),
            usage=AiUsage(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                total_tokens=response.usage.total_tokens,
            ),
            finish_reason=None,
        )
    else:
        return AiGenerationMetadata(
            started_at=timer.started_at,
            completed_at=complete_result[0],
            elapsed_second=complete_result[1].total_seconds(),
            usage=AiUsage(
                input_tokens=response.response.usage.input_tokens,
                output_tokens=response.response.usage.output_tokens,
                total_tokens=response.response.usage.total_tokens,
            ),
            finish_reason=map_pydantic_finish_reason(
                response.response.finish_reason, response.response.state
            ),
        )


def map_generate_text_result(
    timer: ExecutionTimer, response: AgentRunResult[str]
) -> AiGenerateTextResult:
    return AiGenerateTextResult(
        message=AiAssistantMessage(text=response.output, parts=[]),
        metadata=_map_result_metadata(timer, response),
    )


def map_generate_object_result[T: BaseModel](
    timer: ExecutionTimer,
    response: AgentRunResult[T],
) -> AiGenerateObjectResult[T]:
    return AiGenerateObjectResult(
        output=response.output, metadata=_map_result_metadata(timer, response)
    )


def map_embed_result(
    timer: ExecutionTimer,
    response: EmbeddingResult,
) -> AiEmbeddingResult:
    return AiEmbeddingResult(
        output=response.embeddings, metadata=_map_result_metadata(timer, response)
    )
