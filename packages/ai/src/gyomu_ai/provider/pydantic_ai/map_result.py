from collections.abc import Sequence
from decimal import Decimal
from pprint import pprint
from typing import Any

from gyomu_ai.execution.result import (
    AiAssistantTextMessage,
    AiEmbeddingResult,
    AiFinishReason,
    AiGenerateObjectResult,
    AiGenerateTextResult,
    AiGenerationMetadata,
    AiToolCallGroup,
    AiToolCallResultPart,
    AiToolUsage,
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
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ModelResponseState,
    ToolCallPart,
    ToolReturnPart,
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
    finish_reason: AiFinishReason | None
    if isinstance(response, (EmbeddingResult, StreamedRunResult)):
        finish_reason = None

    else:
        # print(response)

        finish_reason = map_pydantic_finish_reason(
            response.response.finish_reason, response.response.state
        )

    if isinstance(response, EmbeddingResult):
        return AiGenerationMetadata(
            started_at=timer.started_at,
            completed_at=complete_result[0],
            elapsed_second=complete_result[1].total_seconds(),
            usage=AiUsage(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                total_tokens=response.usage.total_tokens,
                cost=response.usage.cost,
            ),
            finish_reason=finish_reason,
            tool_calls=None,
        )
    messages = response.all_messages()
    return AiGenerationMetadata(
        started_at=timer.started_at,
        completed_at=complete_result[0],
        elapsed_second=complete_result[1].total_seconds(),
        usage=_calculate_usage(messages),
        finish_reason=finish_reason,
        tool_calls=_build_tool_calls(messages),
    )


def _build_tool_calls(
    messages: Sequence[ModelMessage],
) -> AiToolCallGroup | None:
    calls: list[AiToolCallResultPart] = []
    usage_input_tokens = 0
    usage_output_tokens = 0
    usage_total_tokens = 0

    for index, message in enumerate(messages):
        if not isinstance(message, ModelResponse):
            continue

        tool_call_parts = [
            part for part in message.parts if isinstance(part, ToolCallPart)
        ]

        if not tool_call_parts:
            continue

        usage_input_tokens += message.usage.input_tokens
        usage_output_tokens += message.usage.output_tokens
        usage_total_tokens += message.usage.total_tokens

        tool_returns = _find_tool_returns(
            messages,
            index,
            {part.tool_call_id for part in tool_call_parts},
        )

        for tool_call in tool_call_parts:
            tool_return = tool_returns.get(tool_call.tool_call_id)

            output: Any | None = None
            elapsed_second = 0.0

            if tool_return is not None:
                output = tool_return.content
                elapsed_second = (
                    (tool_return.timestamp - message.timestamp).total_seconds()
                    if tool_return is not None
                    else None
                )

            calls.append(
                AiToolCallResultPart(
                    tool_name=tool_call.tool_name,
                    tool_call_id=tool_call.tool_call_id,
                    input=tool_call.args,
                    output=output,
                    elapsed_second=elapsed_second,
                )
            )

    if not calls:
        return None

    return AiToolCallGroup(
        calls=calls,
        usage=AiToolUsage(
            input_tokens=usage_input_tokens,
            output_tokens=usage_output_tokens,
            total_tokens=usage_total_tokens,
        ),
    )


def _find_tool_returns(
    messages: Sequence[ModelMessage],
    response_index: int,
    tool_call_ids: set[str],
) -> dict[str, ToolReturnPart]:
    result: dict[str, ToolReturnPart] = {}

    for message in messages[response_index + 1 :]:
        if not isinstance(message, ModelRequest):
            continue

        for part in message.parts:
            if isinstance(part, ToolReturnPart) and part.tool_call_id in tool_call_ids:
                result[part.tool_call_id] = part

        if result.keys() >= tool_call_ids:
            break

    return result


def _calculate_usage(messages: Sequence[ModelMessage]) -> AiUsage:
    responses = [message for message in messages if isinstance(message, ModelResponse)]

    input_tokens = sum(response.usage.input_tokens for response in responses)
    output_tokens = sum(response.usage.output_tokens for response in responses)
    total_tokens = sum(response.usage.total_tokens for response in responses)

    costs = [
        response.usage.cost for response in responses if response.usage.cost is not None
    ]

    cost: Decimal | None = sum(costs, Decimal("0")) if costs else None

    return AiUsage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        cost=cost,
    )


def map_generate_text_result(
    timer: ExecutionTimer,
    response: AgentRunResult[str],
    conversation: ConversationSchema,
) -> AiGenerateTextResult:
    assistant_message = MessageSchema.assistant_text(response.output)
    # response.all_messages()
    # print(
    #     json.dumps(
    #         [dataclasses.asdict(request) for request in response.all_messages()],
    #         indent=2,
    #         ensure_ascii=False,
    #         default=str,
    #     )
    # )
    # pprint(response.all_messages(), width=120, sort_dicts=False)
    metadata = _map_result_metadata(timer, response)
    pprint(metadata)

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
