from collections.abc import AsyncIterator
from contextlib import AbstractAsyncContextManager
from types import TracebackType
from typing import Self

from gyomu_ai.execution.result import (
    AiGenerateTextResult,
)
from gyomu_ai.provider.pydantic_ai.map_error import map_pydantic_ai_error
from gyomu_ai.provider.pydantic_ai.map_result import map_stream_text_result
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.error.ai import AiError, AiErrorPhase, AiFailResolution, AiOperation
from gyomu_schema.utility.execution_timer import ExecutionTimer
from pydantic_ai.result import StreamedRunResult


class PydanticAiTextStream:
    def __init__(
        self,
        response: AbstractAsyncContextManager[
            StreamedRunResult[object, str], bool | None
        ],
        conversation: ConversationSchema,
        timer: ExecutionTimer,
        model: str,
        model_key: str,
    ) -> None:
        self._internal_response = response
        self._conversation = conversation
        self._timer = timer
        self._model = model
        self._model_key = model_key

        self._response: StreamedRunResult[object, str] | None = None
        self._stream: AsyncIterator[str] | None = None
        self._text = ""
        self._result: AiGenerateTextResult | None = None

    async def __aenter__(self) -> Self:
        try:
            self._response = await self._internal_response.__aenter__()
            self._stream = self._response.stream_text(delta=True).__aiter__()
            return self
        except Exception as error:
            raise map_pydantic_ai_error(
                error,
                operation=AiOperation.STREAM,
                model_key=self._model_key,
                model=self._model,
            ) from error

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self._internal_response.__aexit__(
            exc_type,
            exc_value,
            traceback,
        )

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> str:
        if self._stream is None:
            raise RuntimeError("Stream is not active")

        try:
            delta = await self._stream.__anext__()
        except StopAsyncIteration:
            await self._complete()
            raise
        except Exception as error:
            raise map_pydantic_ai_error(
                error,
                operation=AiOperation.STREAM,
                model_key=self._model_key,
                model=self._model,
            ) from error

        self._text += delta
        return delta

    async def _complete(self) -> None:
        if self._result is not None:
            return
        if self._response is None:
            raise RuntimeError("Stream is not active")

        try:
            self._result = map_stream_text_result(
                self._timer, self._response, self._text, self._conversation
            )
        except Exception as error:
            raise AiError(
                message="Fail on Stream Result Mapping",
                model=self._model,
                model_key=self._model_key,
                operation=AiOperation.STREAM,
                phase=AiErrorPhase.DECODE,
                resolution=AiFailResolution(),
                context="PydanticAiTextStream._complete",
            ) from error

    @property
    def result(self) -> AiGenerateTextResult | None:
        return self._result
