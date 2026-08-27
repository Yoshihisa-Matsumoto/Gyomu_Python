from gyomu_ai.execution.result import (
    AiAssistantMessage,
    AiFinishReason,
    AiGenerateTextResult,
    AiUsage,
)
from pydantic_ai import AgentRunResult, FinishReason, ModelResponseState


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


def map_generate_text_result(response: AgentRunResult[str]) -> AiGenerateTextResult:
    return AiGenerateTextResult(
        message=AiAssistantMessage(text=response.output, parts=[]),
        usage=AiUsage(
            input_tokens=response.response.usage.input_tokens,
            output_tokens=response.response.usage.output_tokens,
            total_tokens=response.response.usage.total_tokens,
        ),
        finish_reason=map_pydantic_finish_reason(
            response.response.finish_reason, response.response.state
        ),
    )
