from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from gyomu_ai.execution.result import (
    AiEmbeddingResult,
    AiFinishReason,
    AiGenerateObjectResult,
    AiGenerateTextResult,
    AiGenerationMetadata,
    AiToolCallResultPart,
    AiToolUsage,
    AiUsage,
)
from gyomu_ai.provider.pydantic_ai import map_result
from gyomu_ai.provider.pydantic_ai.map_result import (
    _build_tool_calls,
    _calculate_usage,
    _find_tool_returns,
    _map_result_metadata,
    map_pydantic_finish_reason,
)
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import AiTextPart, MessageSchema
from gyomu_schema.utility.execution_timer import ExecutionTimer
from pydantic import BaseModel
from pydantic_ai import (
    FinishReason,
    ModelRequest,
    ModelResponse,
    ModelResponseState,
    RequestUsage,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
)
from pydantic_ai.embeddings import EmbeddingResult


class TestMapPydanticFinishReason:
    @pytest.mark.parametrize(
        ("reason", "state", "expected"),
        [
            ("content_filter", "complete", "content-filtered"),
            ("content_filter", "interrupted", "content-filtered"),
            ("content_filter", "incomplete", "content-filtered"),
            ("error", "complete", "error"),
            ("error", "interrupted", "error"),
            ("error", "incomplete", "error"),
            ("length", "complete", "max-tokens"),
            ("length", "interrupted", "max-tokens"),
            ("length", "incomplete", "max-tokens"),
            ("stop", "complete", "completed"),
            ("stop", "interrupted", "cancelled"),
            ("stop", "incomplete", "error"),
            ("tool_call", "complete", "tool-call"),
            ("tool_call", "interrupted", "tool-call"),
            ("tool_call", "incomplete", "tool-call"),
        ],
    )
    def test_maps_finish_reason(
        self,
        reason: FinishReason,
        state: ModelResponseState,
        expected: AiFinishReason,
    ) -> None:
        assert map_pydantic_finish_reason(reason, state) == expected

    def test_returns_none_when_reason_is_none(
        self,
    ) -> None:
        assert map_pydantic_finish_reason(None, "complete") is None


class TestMapResultMetadata:
    def _create_timer(self) -> MagicMock:
        timer = MagicMock(spec=ExecutionTimer)

        timer.started_at = datetime(
            2026,
            8,
            28,
            10,
            0,
            0,
            tzinfo=UTC,
        )

        timer.complete.return_value = (
            datetime(
                2026,
                8,
                28,
                10,
                0,
                1,
                tzinfo=UTC,
            ),
            timedelta(seconds=1),
        )

        return timer

    def test_maps_agent_run_result(self) -> None:
        timer = self._create_timer()

        response = MagicMock(spec=map_result.AgentRunResult)

        messages = [
            ModelResponse(
                parts=[],
                usage=RequestUsage(
                    input_tokens=10,
                    output_tokens=20,
                ),
                model_name="test",
            ),
        ]

        response.all_messages.return_value = messages
        response.response.finish_reason = "stop"
        response.response.state = "complete"

        metadata = map_result._map_result_metadata(
            timer,
            response,
        )

        assert metadata == AiGenerationMetadata(
            started_at=timer.started_at,
            completed_at=datetime(
                2026,
                8,
                28,
                10,
                0,
                1,
                tzinfo=UTC,
            ),
            elapsed_second=1.0,
            usage=AiUsage(
                input_tokens=10,
                output_tokens=20,
                total_tokens=30,
                cost=None,
            ),
            finish_reason="completed",
            tool_calls=None,
        )

        response.all_messages.assert_called_once()
        timer.complete.assert_called_once()

    def test_maps_embedding_result(self) -> None:
        timer = self._create_timer()

        response = MagicMock(spec=EmbeddingResult)
        response.usage = RequestUsage(
            input_tokens=10,
            output_tokens=0,
        )

        metadata = map_result._map_result_metadata(
            timer,
            response,
        )

        assert metadata == AiGenerationMetadata(
            started_at=timer.started_at,
            completed_at=datetime(
                2026,
                8,
                28,
                10,
                0,
                1,
                tzinfo=UTC,
            ),
            elapsed_second=1.0,
            usage=AiUsage(
                input_tokens=10,
                output_tokens=0,
                total_tokens=10,
                cost=None,
            ),
            finish_reason=None,
            tool_calls=None,
        )

        timer.complete.assert_called_once()

    def test_maps_streamed_run_result(self) -> None:
        timer = self._create_timer()

        response = MagicMock(
            spec=map_result.StreamedRunResult,
        )

        messages = [
            ModelResponse(
                parts=[],
                usage=RequestUsage(
                    input_tokens=50,
                    output_tokens=25,
                ),
                model_name="test",
            ),
        ]

        response.all_messages.return_value = messages

        metadata = map_result._map_result_metadata(
            timer,
            response,
        )

        assert metadata == AiGenerationMetadata(
            started_at=timer.started_at,
            completed_at=datetime(
                2026,
                8,
                28,
                10,
                0,
                1,
                tzinfo=UTC,
            ),
            elapsed_second=1.0,
            usage=AiUsage(
                input_tokens=50,
                output_tokens=25,
                total_tokens=75,
                cost=None,
            ),
            finish_reason=None,
            tool_calls=None,
        )

        response.all_messages.assert_called_once()
        timer.complete.assert_called_once()

    def test_maps_agent_run_result_usage_from_all_messages(self) -> None:
        timer = self._create_timer()

        response = MagicMock(spec=map_result.AgentRunResult)

        response.all_messages.return_value = [
            ModelResponse(
                parts=[],
                usage=RequestUsage(
                    input_tokens=10,
                    output_tokens=20,
                ),
                model_name="test",
            ),
            ModelResponse(
                parts=[],
                usage=RequestUsage(
                    input_tokens=30,
                    output_tokens=40,
                ),
                model_name="test",
            ),
        ]

        response.response.finish_reason = "stop"
        response.response.state = "complete"

        metadata = map_result._map_result_metadata(
            timer,
            response,
        )

        assert metadata.usage == AiUsage(
            input_tokens=40,
            output_tokens=60,
            total_tokens=100,
            cost=None,
        )

    def test_maps_tool_calls(self) -> None:
        timer = MagicMock(spec=ExecutionTimer)

        started_at = datetime(
            2026,
            8,
            30,
            10,
            0,
            0,
            tzinfo=UTC,
        )

        completed_at = datetime(
            2026,
            8,
            30,
            10,
            0,
            3,
            tzinfo=UTC,
        )

        timer.started_at = started_at
        timer.complete.return_value = (
            completed_at,
            timedelta(seconds=3),
        )

        call_timestamp = datetime(
            2026,
            8,
            30,
            10,
            0,
            1,
            tzinfo=UTC,
        )

        return_timestamp = datetime(
            2026,
            8,
            30,
            10,
            0,
            2,
            tzinfo=UTC,
        )

        response = MagicMock(
            spec=map_result.AgentRunResult,
        )

        response.response.finish_reason = "stop"
        response.response.state = "complete"

        response.all_messages.return_value = [
            ModelRequest(parts=[]),
            ModelResponse(
                parts=[
                    ToolCallPart(
                        tool_name="search_file",
                        args={"path": "test.txt"},
                        tool_call_id="call_1",
                    ),
                ],
                usage=RequestUsage(
                    input_tokens=50,
                    output_tokens=10,
                ),
                timestamp=call_timestamp,
            ),
            ModelRequest(
                parts=[
                    ToolReturnPart(
                        tool_name="search_file",
                        content="found",
                        tool_call_id="call_1",
                        timestamp=return_timestamp,
                    ),
                ],
            ),
            ModelResponse(
                parts=[],
                usage=RequestUsage(
                    input_tokens=70,
                    output_tokens=5,
                ),
            ),
        ]

        metadata = _map_result_metadata(
            timer,
            response,
        )

        assert metadata.usage == AiUsage(
            input_tokens=120,
            output_tokens=15,
            total_tokens=135,
            cost=None,
        )

        assert metadata.tool_calls is not None

        assert metadata.tool_calls.calls == [
            AiToolCallResultPart(
                tool_name="search_file",
                tool_call_id="call_1",
                input={"path": "test.txt"},
                output="found",
                elapsed_second=1.0,
            ),
        ]

        assert metadata.tool_calls.usage == AiToolUsage(
            input_tokens=50,
            output_tokens=10,
            total_tokens=60,
        )

        assert metadata.finish_reason == "completed"


class TestMapResultCalculateUsage:
    def test_calculates_usage_from_model_responses(self) -> None:
        messages = [
            ModelRequest(parts=[]),
            ModelResponse(
                parts=[],
                usage=RequestUsage(
                    input_tokens=86,
                    output_tokens=18,
                ),
            ),
            ModelRequest(parts=[]),
            ModelResponse(
                parts=[],
                usage=RequestUsage(
                    input_tokens=124,
                    output_tokens=7,
                ),
            ),
        ]

        result = _calculate_usage(messages)

        assert result == AiUsage(
            input_tokens=210,
            output_tokens=25,
            total_tokens=235,
            cost=None,
        )

    def test_ignores_model_requests(self) -> None:
        messages = [
            ModelRequest(parts=[]),
        ]

        result = _calculate_usage(messages)

        assert result == AiUsage(
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
            cost=None,
        )

    def test_calculates_usage_from_multiple_model_responses(self) -> None:
        messages = [
            ModelResponse(
                parts=[],
                usage=RequestUsage(
                    input_tokens=10,
                    output_tokens=5,
                ),
            ),
            ModelResponse(
                parts=[],
                usage=RequestUsage(
                    input_tokens=20,
                    output_tokens=7,
                ),
            ),
        ]

        result = _calculate_usage(messages)

        assert result == AiUsage(
            input_tokens=30,
            output_tokens=12,
            total_tokens=42,
            cost=None,
        )

    def test_calculates_usage_from_model_responses_with_cost(self) -> None:
        messages = [
            ModelRequest(parts=[]),
            ModelResponse(
                parts=[],
                usage=RequestUsage(
                    input_tokens=86,
                    output_tokens=18,
                    cost=Decimal("0.1"),
                ),
            ),
            ModelRequest(parts=[]),
            ModelResponse(
                parts=[],
                usage=RequestUsage(
                    input_tokens=124,
                    output_tokens=7,
                    cost=Decimal("0.2"),
                ),
            ),
        ]

        result = _calculate_usage(messages)

        assert result == AiUsage(
            input_tokens=210,
            output_tokens=25,
            total_tokens=235,
            cost=Decimal("0.3"),
        )

    def test_returns_none_cost_when_all_responses_have_no_cost(self) -> None:
        messages = [
            ModelResponse(
                parts=[],
                usage=RequestUsage(
                    input_tokens=10,
                    output_tokens=5,
                ),
            ),
            ModelResponse(
                parts=[],
                usage=RequestUsage(
                    input_tokens=20,
                    output_tokens=7,
                ),
            ),
        ]

        result = _calculate_usage(messages)

        assert result == AiUsage(
            input_tokens=30,
            output_tokens=12,
            total_tokens=42,
            cost=None,
        )


class TestFindToolReturns:
    def test_finds_matching_tool_returns(self) -> None:
        tool_call_id = "call_1"

        messages = [
            ModelResponse(
                parts=[
                    ToolCallPart(
                        tool_name="search_file",
                        args={"path": "test.txt"},
                        tool_call_id=tool_call_id,
                    ),
                ],
            ),
            ModelRequest(
                parts=[
                    ToolReturnPart(
                        tool_name="search_file",
                        content="result",
                        tool_call_id=tool_call_id,
                    ),
                ],
            ),
        ]

        result = _find_tool_returns(
            messages,
            response_index=0,
            tool_call_ids={tool_call_id},
        )

        assert result == {
            tool_call_id: messages[1].parts[0],
        }

    def test_ignores_non_matching_tool_returns(self) -> None:
        messages = [
            ModelResponse(
                parts=[
                    ToolCallPart(
                        tool_name="search_file",
                        args={"path": "test.txt"},
                        tool_call_id="call_1",
                    ),
                ],
            ),
            ModelRequest(
                parts=[
                    ToolReturnPart(
                        tool_name="other_tool",
                        content="other",
                        tool_call_id="call_2",
                    ),
                ],
            ),
        ]

        result = _find_tool_returns(
            messages,
            response_index=0,
            tool_call_ids={"call_1"},
        )

        assert result == {}

    def test_finds_multiple_tool_returns(self) -> None:
        messages = [
            ModelResponse(
                parts=[
                    ToolCallPart(
                        tool_name="first",
                        args={"value": 1},
                        tool_call_id="call_1",
                    ),
                    ToolCallPart(
                        tool_name="second",
                        args={"value": 2},
                        tool_call_id="call_2",
                    ),
                ],
            ),
            ModelRequest(
                parts=[
                    ToolReturnPart(
                        tool_name="first",
                        content="result-1",
                        tool_call_id="call_1",
                    ),
                    ToolReturnPart(
                        tool_name="second",
                        content="result-2",
                        tool_call_id="call_2",
                    ),
                ],
            ),
        ]

        result = _find_tool_returns(
            messages,
            response_index=0,
            tool_call_ids={"call_1", "call_2"},
        )

        assert set(result) == {"call_1", "call_2"}
        assert result["call_1"].content == "result-1"
        assert result["call_2"].content == "result-2"


class TestBuildToolCalls:
    def test_returns_none_when_there_are_no_tool_calls(self) -> None:
        messages = [
            ModelRequest(parts=[]),
            ModelResponse(
                parts=[],
                usage=RequestUsage(
                    input_tokens=10,
                    output_tokens=5,
                ),
            ),
        ]

        result = _build_tool_calls(messages)

        assert result is None

    def test_builds_tool_call_result(self) -> None:
        call_timestamp = datetime(
            2026,
            8,
            30,
            10,
            0,
            0,
            tzinfo=UTC,
        )

        return_timestamp = datetime(
            2026,
            8,
            30,
            10,
            0,
            2,
            tzinfo=UTC,
        )

        tool_call = ToolCallPart(
            tool_name="search_file",
            args={
                "path": "test.txt",
            },
            tool_call_id="call_1",
        )

        tool_return = ToolReturnPart(
            tool_name="search_file",
            content="found",
            tool_call_id="call_1",
            timestamp=return_timestamp,
        )

        messages = [
            ModelResponse(
                parts=[tool_call],
                usage=RequestUsage(
                    input_tokens=86,
                    output_tokens=18,
                ),
                timestamp=call_timestamp,
            ),
            ModelRequest(
                parts=[tool_return],
            ),
        ]

        result = _build_tool_calls(messages)

        assert result is not None

        assert len(result.calls) == 1

        call = result.calls[0]

        assert call.tool_name == "search_file"
        assert call.tool_call_id == "call_1"
        assert call.input == {
            "path": "test.txt",
        }
        assert call.output == "found"
        assert call.elapsed_second == 2.0

        assert result.usage == AiToolUsage(
            input_tokens=86,
            output_tokens=18,
            total_tokens=104,
        )

    def test_builds_multiple_tool_calls(self) -> None:
        timestamp = datetime(
            2026,
            8,
            30,
            10,
            0,
            0,
            tzinfo=UTC,
        )

        return_timestamp = datetime(
            2026,
            8,
            30,
            10,
            0,
            1,
            tzinfo=UTC,
        )

        messages = [
            ModelResponse(
                parts=[
                    ToolCallPart(
                        tool_name="first",
                        args={"value": 1},
                        tool_call_id="call_1",
                    ),
                    ToolCallPart(
                        tool_name="second",
                        args={"value": 2},
                        tool_call_id="call_2",
                    ),
                ],
                usage=RequestUsage(
                    input_tokens=100,
                    output_tokens=20,
                ),
                timestamp=timestamp,
            ),
            ModelRequest(
                parts=[
                    ToolReturnPart(
                        tool_name="first",
                        content="result-1",
                        tool_call_id="call_1",
                        timestamp=return_timestamp,
                    ),
                    ToolReturnPart(
                        tool_name="second",
                        content="result-2",
                        tool_call_id="call_2",
                        timestamp=return_timestamp,
                    ),
                ],
            ),
        ]

        result = _build_tool_calls(messages)

        assert result is not None

        assert result.calls == [
            AiToolCallResultPart(
                tool_name="first",
                tool_call_id="call_1",
                input={"value": 1},
                output="result-1",
                elapsed_second=1.0,
            ),
            AiToolCallResultPart(
                tool_name="second",
                tool_call_id="call_2",
                input={"value": 2},
                output="result-2",
                elapsed_second=1.0,
            ),
        ]

        assert result.usage == AiToolUsage(
            input_tokens=100,
            output_tokens=20,
            total_tokens=120,
        )

    def test_builds_tool_call_without_tool_return(self) -> None:
        timestamp = datetime(
            2026,
            8,
            30,
            10,
            0,
            0,
            tzinfo=UTC,
        )

        messages = [
            ModelResponse(
                parts=[
                    ToolCallPart(
                        tool_name="search_file",
                        args={"path": "test.txt"},
                        tool_call_id="call_1",
                    ),
                ],
                usage=RequestUsage(
                    input_tokens=50,
                    output_tokens=10,
                ),
                timestamp=timestamp,
            ),
        ]

        result = _build_tool_calls(messages)

        assert result is not None

        assert result.calls == [
            AiToolCallResultPart(
                tool_name="search_file",
                tool_call_id="call_1",
                input={"path": "test.txt"},
                output=None,
                elapsed_second=0.0,
            ),
        ]

        assert result.usage == AiToolUsage(
            input_tokens=50,
            output_tokens=10,
            total_tokens=60,
        )


class TestMapGenerateTextResult:
    def test_maps_result(self) -> None:
        timer = MagicMock(spec=ExecutionTimer)

        started_at = datetime(
            2026,
            8,
            28,
            10,
            0,
            0,
            tzinfo=UTC,
        )

        completed_at = datetime(
            2026,
            8,
            28,
            10,
            0,
            1,
            tzinfo=UTC,
        )

        timer.started_at = started_at
        timer.complete.return_value = (
            completed_at,
            timedelta(seconds=1),
        )

        response = MagicMock(
            spec=map_result.AgentRunResult,
        )

        response.output = "Hello world"

        response.response.usage.input_tokens = 10
        response.response.usage.output_tokens = 5
        response.response.usage.total_tokens = 15
        response.response.finish_reason = "stop"
        response.response.state = "complete"

        response.all_messages.return_value = [
            ModelRequest(
                parts=[],
            ),
            ModelResponse(
                parts=[
                    TextPart(
                        content="Hello world",
                    ),
                ],
                usage=RequestUsage(
                    input_tokens=10,
                    output_tokens=5,
                ),
                finish_reason="stop",
            ),
        ]

        conversation = ConversationSchema().with_request(
            MessageSchema.user_text("Hello")
        )

        result = map_result.map_generate_text_result(
            timer,
            response,
            conversation,
        )

        assert isinstance(result, AiGenerateTextResult)

        assert result.message.text == "Hello world"

        part = result.message.parts[0]

        assert isinstance(part, AiTextPart)
        assert part.text == "Hello world"

        assert result.metadata == AiGenerationMetadata(
            started_at=started_at,
            completed_at=completed_at,
            elapsed_second=1.0,
            usage=AiUsage(
                input_tokens=10,
                output_tokens=5,
                total_tokens=15,
                cost=None,
            ),
            finish_reason="completed",
            tool_calls=None,
        )

        assert len(result.conversation.messages) == 2
        assert result.conversation.request is None

        assert result.conversation.messages[-1].role.value == "assistant"
        assert result.conversation.messages[-1].parts[0].text == "Hello world"


class TestMapGenerateObjectResult:
    def test_maps_result(self) -> None:
        timer = MagicMock(spec=ExecutionTimer)

        started_at = datetime(
            2026,
            8,
            28,
            10,
            0,
            0,
            tzinfo=UTC,
        )

        completed_at = datetime(
            2026,
            8,
            28,
            10,
            0,
            1,
            tzinfo=UTC,
        )

        timer.started_at = started_at
        timer.complete.return_value = (
            completed_at,
            timedelta(seconds=1),
        )

        class Output(BaseModel):
            name: str
            age: int

        output = Output(
            name="Taro",
            age=30,
        )

        response = MagicMock(
            spec=map_result.AgentRunResult,
        )

        response.output = output

        response.response.usage.input_tokens = 20
        response.response.usage.output_tokens = 10
        response.response.usage.total_tokens = 30
        response.response.finish_reason = "stop"
        response.response.state = "complete"

        response.all_messages.return_value = [
            ModelRequest(
                parts=[],
            ),
            ModelResponse(
                parts=[],
                usage=RequestUsage(
                    input_tokens=20,
                    output_tokens=10,
                ),
                finish_reason="stop",
            ),
        ]

        result = map_result.map_generate_object_result(
            timer,
            response,
        )

        assert isinstance(result, AiGenerateObjectResult)
        assert result.output is output

        assert result.metadata.usage == AiUsage(
            input_tokens=20, output_tokens=10, total_tokens=30, cost=None
        )

        assert result.metadata.finish_reason == "completed"
        assert result.metadata.elapsed_second == 1.0


class TestMapStreamTextResult:
    def test_maps_result(self) -> None:
        timer = MagicMock(spec=ExecutionTimer)

        started_at = datetime(
            2026,
            8,
            28,
            10,
            0,
            0,
            tzinfo=UTC,
        )

        completed_at = datetime(
            2026,
            8,
            28,
            10,
            0,
            1,
            tzinfo=UTC,
        )

        timer.started_at = started_at
        timer.complete.return_value = (
            completed_at,
            timedelta(seconds=1),
        )

        response = MagicMock(
            spec=map_result.StreamedRunResult,
        )

        response.usage.input_tokens = 10
        response.usage.output_tokens = 20
        response.usage.total_tokens = 30

        response.all_messages.return_value = [
            ModelRequest(
                parts=[],
            ),
            ModelResponse(
                parts=[
                    TextPart(
                        content="Hello world",
                    ),
                ],
                usage=RequestUsage(
                    input_tokens=10,
                    output_tokens=20,
                ),
            ),
        ]

        conversation = ConversationSchema().with_request(
            MessageSchema.user_text("Hello")
        )

        result = map_result.map_stream_text_result(
            timer,
            response,
            "Hello world",
            conversation,
        )

        assert isinstance(result, AiGenerateTextResult)

        assert result.message.text == "Hello world"

        part = result.message.parts[0]

        assert isinstance(part, AiTextPart)
        assert part.text == "Hello world"

        assert result.metadata.usage == AiUsage(
            input_tokens=10,
            output_tokens=20,
            total_tokens=30,
            cost=None,
        )

        assert result.metadata.finish_reason is None

        assert len(result.conversation.messages) == 2
        assert result.conversation.request is None


class TestMapEmbedResult:
    def test_maps_result(self) -> None:
        timer = MagicMock(spec=ExecutionTimer)

        started_at = datetime(
            2026,
            8,
            28,
            10,
            0,
            0,
            tzinfo=UTC,
        )

        completed_at = datetime(
            2026,
            8,
            28,
            10,
            0,
            1,
            tzinfo=UTC,
        )

        timer.started_at = started_at
        timer.complete.return_value = (
            completed_at,
            timedelta(seconds=1),
        )

        response = MagicMock(spec=EmbeddingResult)

        vector = [0.1, 0.2, 0.3]

        response.embeddings = vector
        response.usage = RequestUsage(input_tokens=10, output_tokens=0)

        result = map_result.map_embed_result(
            timer,
            response,
        )

        assert isinstance(result, AiEmbeddingResult)

        assert result.vector == vector

        assert result.metadata.usage == AiUsage(
            input_tokens=10, output_tokens=0, total_tokens=10, cost=None
        )

        assert result.metadata.finish_reason is None
        assert result.metadata.elapsed_second == 1.0
