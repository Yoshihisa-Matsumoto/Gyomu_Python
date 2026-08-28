from types import TracebackType
from unittest.mock import AsyncMock, MagicMock

import pytest
from gyomu_ai.execution.result import AiGenerateTextResult
from gyomu_ai.provider.pydantic_ai.result import PydanticAiTextStream
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.utility.execution_timer import ExecutionTimer


class FakeAsyncIterator:
    def __init__(self, values: list[str]) -> None:
        self._values = iter(values)

    def __aiter__(self) -> FakeAsyncIterator:
        return self

    async def __anext__(self) -> str:
        try:
            return next(self._values)
        except StopIteration:
            raise StopAsyncIteration


class TestPydanticAiTextStream:
    def _create_stream(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> tuple[
        PydanticAiTextStream,
        MagicMock,
        MagicMock,
        MagicMock,
    ]:
        response = MagicMock(name="response")

        internal_response = MagicMock(name="internal-response")
        internal_response.__aenter__ = AsyncMock(
            return_value=response,
        )
        internal_response.__aexit__ = AsyncMock()

        conversation = ConversationSchema()
        timer = MagicMock(spec=ExecutionTimer)

        mapped_result = MagicMock(spec=AiGenerateTextResult)

        map_result = MagicMock(
            return_value=mapped_result,
        )
        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.result.map_stream_text_result",
            map_result,
        )

        text_stream = PydanticAiTextStream(
            internal_response,
            conversation,
            timer,
        )

        return (
            text_stream,
            internal_response,
            response,
            map_result,
        )

    @pytest.mark.asyncio
    async def test_aenter(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        (
            stream,
            internal_response,
            response,
            _,
        ) = self._create_stream(monkeypatch)

        result = await stream.__aenter__()

        assert result is stream

        internal_response.__aenter__.assert_awaited_once_with()

        response.stream_text.assert_called_once_with(
            delta=True,
        )

    @pytest.mark.asyncio
    async def test_streams_deltas_in_order(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        (
            stream,
            _,
            response,
            _,
        ) = self._create_stream(monkeypatch)

        source = FakeAsyncIterator(
            [
                "Hello",
                " world",
                "!",
            ],
        )

        response.stream_text.return_value = source

        async with stream:
            deltas = [delta async for delta in stream]

        assert deltas == [
            "Hello",
            " world",
            "!",
        ]

    @pytest.mark.asyncio
    async def test_completes_result_after_stream_ends(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        (
            stream,
            _,
            response,
            map_result,
        ) = self._create_stream(monkeypatch)

        source = FakeAsyncIterator(
            [
                "Hello",
                " world",
                "!",
            ],
        )

        response.stream_text.return_value = source

        assert stream.result is None

        async with stream:
            assert await stream.__anext__() == "Hello"
            assert await stream.__anext__() == " world"
            assert await stream.__anext__() == "!"

            with pytest.raises(StopAsyncIteration):
                await stream.__anext__()

        assert stream.result is map_result.return_value

        map_result.assert_called_once_with(
            stream._timer,
            response,
            "Hello world!",
            stream._conversation,
        )

    @pytest.mark.asyncio
    async def test_complete_is_idempotent(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        (
            stream,
            _,
            response,
            map_result,
        ) = self._create_stream(monkeypatch)

        await stream.__aenter__()

        stream._text = "Hello"

        await stream._complete()
        await stream._complete()

        assert stream.result is map_result.return_value

        map_result.assert_called_once_with(
            stream._timer,
            response,
            "Hello",
            stream._conversation,
        )

    @pytest.mark.asyncio
    async def test_anext_rejects_before_aenter(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        (
            stream,
            _,
            _,
            _,
        ) = self._create_stream(monkeypatch)

        with pytest.raises(
            RuntimeError,
            match="Stream is not active",
        ):
            await stream.__anext__()

    @pytest.mark.asyncio
    async def test_complete_rejects_before_aenter(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        (
            stream,
            _,
            _,
            _,
        ) = self._create_stream(monkeypatch)

        with pytest.raises(
            RuntimeError,
            match="Stream is not active",
        ):
            await stream._complete()

    @pytest.mark.asyncio
    async def test_aexit_delegates_to_internal_response(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        (
            stream,
            internal_response,
            _,
            _,
        ) = self._create_stream(monkeypatch)

        exc_type = ValueError
        exc_value = ValueError("test error")
        traceback = MagicMock(spec=TracebackType)

        await stream.__aexit__(
            exc_type,
            exc_value,
            traceback,
        )

        internal_response.__aexit__.assert_awaited_once_with(
            exc_type,
            exc_value,
            traceback,
        )

    @pytest.mark.asyncio
    async def test_aexit_propagates_exception(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        (
            stream,
            internal_response,
            _,
            _,
        ) = self._create_stream(monkeypatch)

        internal_response.__aexit__.side_effect = RuntimeError(
            "exit error",
        )

        with pytest.raises(
            RuntimeError,
            match="exit error",
        ):
            await stream.__aexit__(
                None,
                None,
                None,
            )

    @pytest.mark.asyncio
    async def test_aexit_receives_exception(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        (
            stream,
            internal_response,
            _,
            _,
        ) = self._create_stream(monkeypatch)

        try:
            async with stream:
                raise ValueError("test error")
        except ValueError:
            pass

        internal_response.__aexit__.assert_awaited_once()

        args = internal_response.__aexit__.await_args.args

        assert args[0] is ValueError
        assert isinstance(args[1], ValueError)
        assert str(args[1]) == "test error"
        assert args[2] is not None
