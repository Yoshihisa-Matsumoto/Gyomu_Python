from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest
from gyomu_ai.execution.result import (
    AiEmbeddingResult,
    AiFinishReason,
    AiGenerateObjectResult,
    AiGenerateTextResult,
    AiGenerationMetadata,
    AiUsage,
)
from gyomu_ai.provider.pydantic_ai import map_result
from gyomu_ai.provider.pydantic_ai.map_result import (
    map_pydantic_finish_reason,
)
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import AiTextPart, MessageSchema
from gyomu_schema.utility.execution_timer import ExecutionTimer
from pydantic import BaseModel
from pydantic_ai import FinishReason, ModelResponseState, RequestUsage
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

        response.response.usage.input_tokens = 10
        response.response.usage.output_tokens = 20
        response.response.usage.total_tokens = 30

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
            ),
            finish_reason="completed",
        )

        timer.complete.assert_called_once()

    def test_maps_embedding_result(self) -> None:
        timer = self._create_timer()
        response = MagicMock(spec=EmbeddingResult)
        response.usage = RequestUsage(input_tokens=10, output_tokens=0)

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
            ),
            finish_reason=None,
        )

    def test_maps_streamed_run_result(self) -> None:
        timer = self._create_timer()

        response = MagicMock(
            spec=map_result.StreamedRunResult,
        )

        response.usage.input_tokens = 50
        response.usage.output_tokens = 25
        response.usage.total_tokens = 75

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
            ),
            finish_reason=None,
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
            ),
            finish_reason="completed",
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

        result = map_result.map_generate_object_result(
            timer,
            response,
        )

        assert isinstance(result, AiGenerateObjectResult)
        assert result.output is output

        assert result.metadata.usage == AiUsage(
            input_tokens=20,
            output_tokens=10,
            total_tokens=30,
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
            input_tokens=10,
            output_tokens=0,
            total_tokens=10,
        )

        assert result.metadata.finish_reason is None
        assert result.metadata.elapsed_second == 1.0
