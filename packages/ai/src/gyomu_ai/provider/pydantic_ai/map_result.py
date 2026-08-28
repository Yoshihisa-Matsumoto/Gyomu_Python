from gyomu_ai.execution.result import (
    AiAssistantTextMessage,
    AiEmbeddingResult,
    AiFinishReason,
    AiGenerateObjectResult,
    AiGenerateTextResult,
    AiGenerationMetadata,
    AiUsage,
)
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import MessageSchema
from gyomu_schema.utility.execution_timer import ExecutionTimer
from pydantic import BaseModel
from pydantic_ai import (
    AgentRunResult,
    EmbeddingResult,
    FinishReason,
    ModelResponseState,
)
from pydantic_ai.result import StreamedRunResult


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
    timer: ExecutionTimer,
    response: AgentRunResult[T] | EmbeddingResult | StreamedRunResult[object, str],
) -> AiGenerationMetadata:
    complete_result = timer.complete()
    if isinstance(response, EmbeddingResult) or isinstance(response, StreamedRunResult):
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
    timer: ExecutionTimer,
    response: AgentRunResult[str],
    conversation: ConversationSchema,
) -> AiGenerateTextResult:
    assistant_message = MessageSchema.assistant_text(response.output)

    conversation = conversation.complete(assistant_message)
    return AiGenerateTextResult(
        message=AiAssistantTextMessage.from_message(assistant_message),
        conversation=conversation,
        metadata=_map_result_metadata(timer, response),
    )


def map_generate_object_result[T: BaseModel](
    timer: ExecutionTimer,
    response: AgentRunResult[T],
) -> AiGenerateObjectResult[T]:
    return AiGenerateObjectResult(
        output=response.output, metadata=_map_result_metadata(timer, response)
    )


def map_stream_text_result(
    timer: ExecutionTimer,
    response: StreamedRunResult[object, str],
    total_text: str,
    conversation: ConversationSchema,
) -> AiGenerateTextResult:

    assistant_message = MessageSchema.assistant_text(total_text)

    conversation = conversation.complete(
        assistant_message,
    )

    message = AiAssistantTextMessage.from_message(
        assistant_message,
    )

    metadata = _map_result_metadata(timer, response)

    return AiGenerateTextResult(
        message=message,
        metadata=metadata,
        conversation=conversation,
    )


def map_embed_result(
    timer: ExecutionTimer,
    response: EmbeddingResult,
) -> AiEmbeddingResult:
    return AiEmbeddingResult(
        vector=response.embeddings, metadata=_map_result_metadata(timer, response)
    )
