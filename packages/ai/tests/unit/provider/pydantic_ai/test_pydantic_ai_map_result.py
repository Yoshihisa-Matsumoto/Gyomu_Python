from unittest.mock import Mock

import pytest
from gyomu_ai.execution.result import AiFinishReason
from gyomu_ai.provider.pydantic_ai.map_result import (
    map_generate_text_result,
    map_pydantic_finish_reason,
)
from pydantic_ai import AgentRunResult, FinishReason, ModelResponseState


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


class TestMapGenerateTextResult:
    def test_maps_generate_text_result(self) -> None:
        usage = Mock()
        usage.input_tokens = 10.0
        usage.output_tokens = 20.0
        usage.total_tokens = 30.0

        response = Mock()
        response.output = "Hello"
        response.usage = usage
        response.finish_reason = "stop"
        response.state = "complete"

        agent_result = Mock(spec=AgentRunResult)
        agent_result.output = response.output
        agent_result.response = response

        result = map_generate_text_result(agent_result)

        assert result.message.text == "Hello"
        assert result.message.parts == []
        assert result.usage is not None
        assert result.usage.input_tokens == 10.0
        assert result.usage.output_tokens == 20.0
        assert result.usage.total_tokens == 30.0
        assert result.finish_reason == "completed"
