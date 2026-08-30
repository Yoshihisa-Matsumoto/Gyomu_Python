from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock

import pytest
from gyomu_ai.execution.context import AiModelContext
from gyomu_ai.execution.parameter import (
    AiEmbeddingMode,
    EmbedParams,
    GenerateObjectParams,
    GenerateTextParams,
    StreamTextParams,
    ToolConfig,
    ToolLoopPolicyMaxSteps,
)
from gyomu_ai.execution.result import (
    AiEmbeddingResult,
    AiGenerateObjectResult,
    AiGenerateTextResult,
)
from gyomu_ai.model.ai_model import AiModelKey
from gyomu_ai.provider.pydantic_ai.ai_model import PydanticAiModelRegistry
from gyomu_ai.provider.pydantic_ai.create_agent import create_pydantic_ai_agent
from gyomu_ai.provider.pydantic_ai.execution import PydanticAiModelExecution
from gyomu_ai.provider.pydantic_ai.stream import PydanticAiTextStream
from gyomu_ai.tool.ai_tool import (
    AiTool,
    PublicError,
    ToolFailureResult,
    ToolResult,
    ToolSuccessResult,
)
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import MessageSchema
from gyomu_schema.error.ai import AiError, AiErrorPhase, AiOperation
from pydantic import BaseModel
from pydantic_ai import ModelHTTPError, UsageLimits
from pydantic_ai.models import Model
from pydantic_ai.models.test import TestModel
from returns.result import Failure, Success


@dataclass(frozen=True)
class DummyOutput(BaseModel):
    value: str


@pytest.fixture
def model_registry() -> PydanticAiModelRegistry:
    fast = MagicMock(name="fast-model")
    smart = MagicMock(name="smart-model")
    reasoning = MagicMock(name="reasoning-model")
    vision = MagicMock(name="vision-model")
    embedding = MagicMock(name="embedding-model")

    return PydanticAiModelRegistry(
        fast=MagicMock(return_value=fast),
        smart=MagicMock(return_value=smart),
        reasoning=MagicMock(return_value=reasoning),
        vision=MagicMock(return_value=vision),
        embedding=MagicMock(return_value=embedding),
    )


class TestPydanticAiModelExecution_SelectModel:
    @pytest.mark.parametrize(
        ("key", "factory_name"),
        [
            (AiModelKey.FAST, "fast"),
            (AiModelKey.SMART, "smart"),
            (AiModelKey.REASONING, "reasoning"),
            (AiModelKey.VISION, "vision"),
        ],
    )
    def test_select_model(
        self,
        key: AiModelKey,
        factory_name: str,
        model_registry: PydanticAiModelRegistry,
    ) -> None:
        execution = PydanticAiModelExecution(model_registry)

        context = MagicMock(spec=AiModelContext)

        model = execution._select_model(key, context)

        factory = getattr(model_registry, factory_name)
        assert model is factory.return_value
        factory.assert_called_once_with(context)

    def test_select_model_rejects_embedding(
        self,
        model_registry: PydanticAiModelRegistry,
    ) -> None:
        execution = PydanticAiModelExecution(model_registry)

        with pytest.raises(ValueError, match="Embedding model cannot be used"):
            execution._select_model(
                AiModelKey.EMBEDDING,
                None,
            )


class TestPydanticAiModelExecution_GenerateText:
    @pytest.mark.asyncio
    async def test_generate_text(
        self,
        monkeypatch: pytest.MonkeyPatch,
        model_registry: PydanticAiModelRegistry,
    ) -> None:
        model = MagicMock(name="model")

        def fast_factory(
            context: AiModelContext | None,
        ) -> Model:
            return model

        model_registry = PydanticAiModelRegistry(
            fast=fast_factory,
            smart=lambda _: MagicMock(),
            reasoning=lambda _: MagicMock(),
            vision=lambda _: MagicMock(),
            embedding=lambda _: MagicMock(),
        )

        prompt = MagicMock(
            instructions="system",
            user_prompt="user",
            message_history=[],
        )
        model_settings = {"temperature": 0.5}
        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.build_prompt",
            MagicMock(return_value=prompt),
        )

        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.build_model_settings",
            MagicMock(return_value=model_settings),
        )

        response = MagicMock(name="response")

        agent = MagicMock()
        agent.run = AsyncMock(return_value=response)

        usage_limits = MagicMock(spec=UsageLimits)

        create_agent = MagicMock(
            return_value=(agent, usage_limits),
        )

        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.create_pydantic_ai_agent",
            create_agent,
        )

        mapped_result = MagicMock(spec=AiGenerateTextResult)
        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.map_generate_text_result",
            MagicMock(return_value=mapped_result),
        )

        execution = PydanticAiModelExecution(model_registry)

        conversation = ConversationSchema().with_request(
            MessageSchema.user_text("request")
        )
        params = GenerateTextParams(
            key=AiModelKey.FAST,
            execution=MagicMock(),
        )

        result = await execution.generate_text(
            conversation,
            params,
        )

        assert isinstance(result, Success)

        create_agent.assert_called_once_with(
            model,
            params.tool,
        )

        agent.run.assert_awaited_once_with(
            instructions=prompt.instructions,
            user_prompt=prompt.user_prompt,
            message_history=prompt.message_history,
            model_settings=model_settings,
            usage_limits=usage_limits,
        )

        assert isinstance(
            result.unwrap(),
            AiGenerateTextResult,
        )

    @pytest.mark.asyncio
    async def test_generate_text_maps_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
        model_registry: PydanticAiModelRegistry,
    ) -> None:
        model = MagicMock(name="model")

        def fast_factory(
            context: AiModelContext | None,
        ) -> Model:
            return model

        model_registry = PydanticAiModelRegistry(
            fast=fast_factory,
            smart=lambda _: MagicMock(),
            reasoning=lambda _: MagicMock(),
            vision=lambda _: MagicMock(),
            embedding=lambda _: MagicMock(),
        )

        error = ModelHTTPError(
            status_code=429,
            model_name="gemini-3.5-flash-lite",
            body={
                "error": {
                    "code": 429,
                    "message": "Too many requests",
                },
            },
        )

        agent = MagicMock()
        agent.run = AsyncMock(side_effect=error)

        usage_limits = MagicMock(spec=UsageLimits)

        create_agent = MagicMock(
            return_value=(agent, usage_limits),
        )

        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.create_pydantic_ai_agent",
            create_agent,
        )

        execution = PydanticAiModelExecution(model_registry)

        conversation = ConversationSchema().with_request(
            MessageSchema.user_text("request")
        )
        params = GenerateTextParams(
            key=AiModelKey.FAST,
            execution=MagicMock(),
        )

        result = await execution.generate_text(
            conversation,
            params,
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, AiError)
        assert error.operation is AiOperation.GENERATE
        assert error.model_key == AiModelKey.FAST.value
        assert error.model == "gemini-3.5-flash-lite"
        assert error.phase is AiErrorPhase.RATE_LIMIT
        assert error.status_code == 429

    @pytest.mark.asyncio
    async def test_generate_text_with_tool(
        self,
        model_registry: PydanticAiModelRegistry,
    ) -> None:
        execute = AsyncMock(
            return_value=ToolSuccessResult(
                data=3,
            ),
        )

        async def execute_tool(
            input: AddInput,
            config: TestToolConfig | None,
        ) -> ToolResult[int]:
            return await execute(input, config)

        tool = AiTool(
            name="add",
            description="Add two numbers.",
            input_type=AddInput,
            config=None,
            execute=execute_tool,
        )

        tool_config = ToolConfig(
            tool_loop_policy=ToolLoopPolicyMaxSteps(
                max_steps=1,
            ),
            tools=[tool],
        )

        model = TestModel(
            call_tools=["add"],
        )

        model_registry = PydanticAiModelRegistry(
            fast=lambda _: model,
            smart=lambda _: MagicMock(),
            reasoning=lambda _: MagicMock(),
            vision=lambda _: MagicMock(),
            embedding=lambda _: MagicMock(),
        )

        execution = PydanticAiModelExecution(model_registry)

        conversation = ConversationSchema().with_request(
            MessageSchema.user_text("Add two numbers.")
        )

        params = GenerateTextParams(
            key=AiModelKey.FAST,
            tool=tool_config,
        )

        result = await execution.generate_text(
            conversation,
            params,
        )

        assert isinstance(result, Success)

        execute.assert_awaited_once()

        assert execute.await_args
        input_value = execute.await_args.args[0]

        assert input_value == AddInput(
            left=0,
            right=0,
        )

        assert execute.await_args.args[1] is None

        assert isinstance(
            result.unwrap(),
            AiGenerateTextResult,
        )

    @pytest.mark.asyncio
    async def test_generate_text_with_tool_max_steps(
        self,
        model_registry: PydanticAiModelRegistry,
    ) -> None:
        execute = AsyncMock(
            return_value=ToolSuccessResult(
                data=3,
            ),
        )

        async def execute_tool(
            input: AddInput,
            config: TestToolConfig | None,
        ) -> ToolResult[int]:
            return await execute(input, config)

        tool = AiTool(
            name="add",
            description="Add two numbers.",
            input_type=AddInput,
            config=None,
            execute=execute_tool,
        )

        tool_config = ToolConfig(
            tool_loop_policy=ToolLoopPolicyMaxSteps(
                max_steps=1,
            ),
            tools=[tool],
        )

        model = TestModel(
            call_tools=["add"],
        )

        model_registry = PydanticAiModelRegistry(
            fast=lambda _: model,
            smart=lambda _: MagicMock(),
            reasoning=lambda _: MagicMock(),
            vision=lambda _: MagicMock(),
            embedding=lambda _: MagicMock(),
        )

        execution = PydanticAiModelExecution(model_registry)

        conversation = ConversationSchema().with_request(
            MessageSchema.user_text("Add two numbers.")
        )

        params = GenerateTextParams(
            key=AiModelKey.FAST,
            tool=tool_config,
        )

        result = await execution.generate_text(
            conversation,
            params,
        )

        assert isinstance(result, Success)

        execute.assert_awaited_once()


class TestPydanticAiModelExecution_GenerateObject:
    @pytest.mark.asyncio
    async def test_generate_object(
        self,
        monkeypatch: pytest.MonkeyPatch,
        model_registry: PydanticAiModelRegistry,
    ) -> None:
        model = MagicMock(name="model")

        def smart_factory(
            context: AiModelContext | None,
        ) -> Model:
            return model

        model_registry = PydanticAiModelRegistry(
            fast=lambda _: MagicMock(),
            smart=smart_factory,
            reasoning=lambda _: MagicMock(),
            vision=lambda _: MagicMock(),
            embedding=lambda _: MagicMock(),
        )

        prompt = MagicMock(
            instructions="system",
            user_prompt="user",
            message_history=[],
        )
        model_settings = {"temperature": 0.5}
        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.build_prompt",
            MagicMock(return_value=prompt),
        )

        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.build_model_settings",
            MagicMock(return_value=model_settings),
        )

        response = MagicMock(name="response")
        agent = MagicMock()
        agent.run = AsyncMock(return_value=response)

        usage_limits = MagicMock(spec=UsageLimits)

        create_agent = MagicMock(
            return_value=(agent, usage_limits),
        )

        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.create_pydantic_ai_agent_for_object",
            create_agent,
        )

        mapped_result = MagicMock(spec=AiGenerateObjectResult)

        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.map_generate_object_result",
            MagicMock(return_value=mapped_result),
        )

        execution = PydanticAiModelExecution(model_registry)

        conversation = ConversationSchema()

        params = GenerateObjectParams(
            key=AiModelKey.SMART,
            execution=MagicMock(),
            output_type=DummyOutput,
        )

        result = await execution.generate_object(
            conversation,
            params,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is mapped_result

        create_agent.assert_called_once_with(
            model,
            DummyOutput,
            None,
        )

        agent.run.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_generate_object_maps_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
        model_registry: PydanticAiModelRegistry,
    ) -> None:
        model = MagicMock(name="model")

        def smart_factory(
            context: AiModelContext | None,
        ) -> Model:
            return model

        model_registry = PydanticAiModelRegistry(
            fast=lambda _: MagicMock(),
            smart=smart_factory,
            reasoning=lambda _: MagicMock(),
            vision=lambda _: MagicMock(),
            embedding=lambda _: MagicMock(),
        )
        prompt = MagicMock(
            instructions="system",
            user_prompt="user",
            message_history=[],
        )
        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.build_prompt",
            MagicMock(return_value=prompt),
        )

        error = ModelHTTPError(
            status_code=429,
            model_name="gemini-3.5-flash-lite",
            body={
                "error": {
                    "code": 429,
                    "message": "Too many requests",
                },
            },
        )

        agent = MagicMock()
        agent.run = AsyncMock(side_effect=error)

        usage_limits = MagicMock(spec=UsageLimits)

        create_agent = MagicMock(
            return_value=(agent, usage_limits),
        )

        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.create_pydantic_ai_agent_for_object",
            create_agent,
        )

        execution = PydanticAiModelExecution(model_registry)

        conversation = ConversationSchema()

        params = GenerateObjectParams(
            key=AiModelKey.SMART,
            execution=MagicMock(),
            output_type=DummyOutput,
        )

        result = await execution.generate_object(
            conversation,
            params,
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, AiError)
        assert error.operation is AiOperation.GENERATE
        assert error.model_key == AiModelKey.SMART.value
        assert error.model == "gemini-3.5-flash-lite"
        assert error.phase is AiErrorPhase.RATE_LIMIT
        assert error.status_code == 429

    @pytest.mark.asyncio
    async def test_generate_object_with_tool(
        self,
        model_registry: PydanticAiModelRegistry,
    ) -> None:
        model = TestModel(
            call_tools=["add"],
        )

        model_registry = PydanticAiModelRegistry(
            fast=lambda _: MagicMock(),
            smart=lambda _: model,
            reasoning=lambda _: MagicMock(),
            vision=lambda _: MagicMock(),
            embedding=lambda _: MagicMock(),
        )

        execute = AsyncMock(
            return_value=ToolSuccessResult(
                data=3,
            ),
        )

        async def execute_tool(
            input: AddInput,
            config: TestToolConfig | None,
        ) -> ToolResult[int]:
            return await execute(input, config)

        tool = AiTool(
            name="add",
            description="Add two numbers.",
            input_type=AddInput,
            config=None,
            execute=execute_tool,
        )

        tool_config = ToolConfig(
            tool_loop_policy=ToolLoopPolicyMaxSteps(
                max_steps=1,
            ),
            tools=[tool],
        )

        execution = PydanticAiModelExecution(model_registry)

        conversation = ConversationSchema().with_request(
            MessageSchema.user_text("Use the add tool to calculate a value.")
        )

        params = GenerateObjectParams(
            key=AiModelKey.SMART,
            execution=MagicMock(),
            output_type=DummyOutput,
            tool=tool_config,
        )

        result = await execution.generate_object(
            conversation,
            params,
        )

        assert isinstance(result, Success)

        execute.assert_awaited_once()

        assert execute.await_args
        input_value = execute.await_args.args[0]

        assert input_value == AddInput(
            left=0,
            right=0,
        )

        assert execute.await_args.args[1] is None

        assert isinstance(
            result.unwrap(),
            AiGenerateObjectResult,
        )


class TestPydanticAiModelExecution_StreamText:
    @pytest.mark.asyncio
    async def test_stream_text(
        self,
        monkeypatch: pytest.MonkeyPatch,
        model_registry: PydanticAiModelRegistry,
    ) -> None:
        model = MagicMock(name="model")

        def reasoning_factory(
            context: AiModelContext | None,
        ) -> Model:
            return model

        model_registry = PydanticAiModelRegistry(
            fast=lambda _: MagicMock(),
            smart=lambda _: MagicMock(),
            reasoning=reasoning_factory,
            vision=lambda _: MagicMock(),
            embedding=lambda _: MagicMock(),
        )

        prompt = MagicMock(
            instructions="system",
            user_prompt="user",
            message_history=[],
        )
        model_settings = {"temperature": 0.5}
        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.build_prompt",
            MagicMock(return_value=prompt),
        )

        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.build_model_settings",
            MagicMock(return_value=model_settings),
        )

        response = MagicMock(name="response")

        agent = MagicMock()
        agent.run_stream.return_value = response

        usage_limits = MagicMock(spec=UsageLimits)

        create_agent = MagicMock(
            return_value=(agent, usage_limits),
        )

        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.create_pydantic_ai_agent",
            create_agent,
        )

        execution = PydanticAiModelExecution(model_registry)

        conversation = ConversationSchema()

        params = StreamTextParams(
            key=AiModelKey.REASONING,
            execution=MagicMock(),
        )

        result = await execution.stream_text(
            conversation,
            params,
        )

        assert isinstance(result, Success)

        stream = result.unwrap()

        assert isinstance(stream, PydanticAiTextStream)

        create_agent.assert_called_once_with(model, None)

        agent.run_stream.assert_called_once()

    @pytest.mark.asyncio
    async def test_stream_text_maps_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
        model_registry: PydanticAiModelRegistry,
    ) -> None:
        model = MagicMock(name="model")

        def reasoning_factory(
            context: AiModelContext | None,
        ) -> Model:
            return model

        model_registry = PydanticAiModelRegistry(
            fast=lambda _: MagicMock(),
            smart=lambda _: MagicMock(),
            reasoning=reasoning_factory,
            vision=lambda _: MagicMock(),
            embedding=lambda _: MagicMock(),
        )

        prompt = MagicMock(
            instructions="system",
            user_prompt="user",
            message_history=[],
        )
        model_settings = {"temperature": 0.5}

        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.build_prompt",
            MagicMock(return_value=prompt),
        )

        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.build_model_settings",
            MagicMock(return_value=model_settings),
        )

        error = ModelHTTPError(
            status_code=429,
            model_name="gemini-3.5-flash-lite",
            body={
                "error": {
                    "code": 429,
                    "message": "Too many requests",
                },
            },
        )

        agent = MagicMock()
        agent.run_stream.side_effect = error

        usage_limits = MagicMock(spec=UsageLimits)

        create_agent = MagicMock(
            return_value=(agent, usage_limits),
        )

        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.create_pydantic_ai_agent",
            create_agent,
        )

        execution = PydanticAiModelExecution(model_registry)

        conversation = ConversationSchema()

        params = StreamTextParams(
            key=AiModelKey.REASONING,
            execution=MagicMock(),
        )

        result = await execution.stream_text(
            conversation,
            params,
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, AiError)
        assert error.operation is AiOperation.STREAM
        assert error.model_key == AiModelKey.REASONING.value
        assert error.model == "gemini-3.5-flash-lite"
        assert error.phase is AiErrorPhase.RATE_LIMIT
        assert error.status_code == 429

        create_agent.assert_called_once_with(model, None)

        agent.run_stream.assert_called_once_with(
            instructions=prompt.instructions,
            user_prompt=prompt.user_prompt,
            message_history=prompt.message_history,
            model_settings=model_settings,
            usage_limits=usage_limits,
        )

    @pytest.mark.asyncio
    async def test_stream_text_with_tool(
        self,
        monkeypatch: pytest.MonkeyPatch,
        model_registry: PydanticAiModelRegistry,
    ) -> None:
        model = MagicMock(name="model")

        def reasoning_factory(
            context: AiModelContext | None,
        ) -> Model:
            return model

        model_registry = PydanticAiModelRegistry(
            fast=lambda _: MagicMock(),
            smart=lambda _: MagicMock(),
            reasoning=reasoning_factory,
            vision=lambda _: MagicMock(),
            embedding=lambda _: MagicMock(),
        )

        prompt = MagicMock(
            instructions="system",
            user_prompt="user",
            message_history=[],
        )

        model_settings = {"temperature": 0.5}

        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.build_prompt",
            MagicMock(return_value=prompt),
        )

        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.build_model_settings",
            MagicMock(return_value=model_settings),
        )

        response = MagicMock(name="response")

        agent = MagicMock()
        agent.run_stream.return_value = response

        usage_limits = MagicMock(spec=UsageLimits)

        create_agent = MagicMock(
            return_value=(agent, usage_limits),
        )

        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.create_pydantic_ai_agent",
            create_agent,
        )

        execute = AsyncMock(
            return_value=ToolSuccessResult(
                data=3,
            ),
        )

        async def execute_tool(
            input: AddInput,
            config: TestToolConfig | None,
        ) -> ToolResult[int]:
            return await execute(input, config)

        tool = AiTool(
            name="add",
            description="Add two numbers.",
            input_type=AddInput,
            config=None,
            execute=execute_tool,
        )

        tool_config = ToolConfig(
            tool_loop_policy=ToolLoopPolicyMaxSteps(
                max_steps=1,
            ),
            tools=[tool],
        )

        execution = PydanticAiModelExecution(model_registry)

        conversation = ConversationSchema()

        params = StreamTextParams(
            key=AiModelKey.REASONING,
            execution=MagicMock(),
            tool=tool_config,
        )

        result = await execution.stream_text(
            conversation,
            params,
        )

        assert isinstance(result, Success)

        stream = result.unwrap()

        assert isinstance(stream, PydanticAiTextStream)

        create_agent.assert_called_once()

        call = create_agent.call_args

        assert call.args[0] is model
        used_tool_config = call.args[1]
        assert used_tool_config is tool_config

        agent.run_stream.assert_called_once()


class TestPydanticAiModelExecution_Embed:
    @pytest.mark.asyncio
    async def test_embed(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        embedding_agent = MagicMock(name="embedding-agent")
        embedding_agent.embed = AsyncMock(
            return_value=MagicMock(name="response"),
        )

        embedding_factory = MagicMock(
            return_value=embedding_agent,
        )

        model_registry = PydanticAiModelRegistry(
            fast=lambda _: MagicMock(),
            smart=lambda _: MagicMock(),
            reasoning=lambda _: MagicMock(),
            vision=lambda _: MagicMock(),
            embedding=embedding_factory,
        )

        mapped_result = MagicMock(spec=AiEmbeddingResult)

        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.map_embed_result",
            MagicMock(return_value=mapped_result),
        )

        execution = PydanticAiModelExecution(model_registry)

        params = EmbedParams(
            execution=MagicMock(),
            value="hello world",
            mode=AiEmbeddingMode.QUERY,
        )

        result = await execution.embed(params)

        assert isinstance(result, Success)
        assert result.unwrap() is mapped_result

        embedding_factory.assert_called_once_with(
            params.execution,
        )

        embedding_agent.embed.assert_awaited_once_with(
            "hello world",
            input_type="query",
        )

    @pytest.mark.asyncio
    async def test_embed_maps_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        embedding_agent = MagicMock(name="embedding-agent")

        error = ModelHTTPError(
            status_code=429,
            model_name="gemini-embedding-001",
            body={
                "error": {
                    "code": 429,
                    "message": "Too many requests",
                },
            },
        )

        embedding_agent.embed = AsyncMock(
            side_effect=error,
        )

        embedding_factory = MagicMock(
            return_value=embedding_agent,
        )

        model_registry = PydanticAiModelRegistry(
            fast=lambda _: MagicMock(),
            smart=lambda _: MagicMock(),
            reasoning=lambda _: MagicMock(),
            vision=lambda _: MagicMock(),
            embedding=embedding_factory,
        )

        execution = PydanticAiModelExecution(model_registry)

        params = EmbedParams(
            execution=MagicMock(),
            value="hello world",
            mode=AiEmbeddingMode.QUERY,
        )

        result = await execution.embed(params)

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, AiError)
        assert error.operation is AiOperation.EMBEDDING
        assert error.model_key == AiModelKey.EMBEDDING
        assert error.model == "gemini-embedding-001"
        assert error.phase is AiErrorPhase.RATE_LIMIT
        assert error.status_code == 429

        embedding_factory.assert_called_once_with(
            params.execution,
        )

        embedding_agent.embed.assert_awaited_once_with(
            "hello world",
            input_type="query",
        )


class AddInput(BaseModel):
    left: int
    right: int


class TestToolConfig(BaseModel):
    pass


class TestPydanticAiToolCall:
    @pytest.mark.asyncio
    async def test_calls_ai_tool(self) -> None:
        execute = AsyncMock(
            return_value=ToolSuccessResult(
                data=3,
            )
        )

        async def execute_tool(
            input: AddInput,
            config: TestToolConfig | None,
        ) -> ToolResult[int]:
            return await execute(input, config)

        tool = AiTool(
            name="add",
            description="Add two numbers.",
            input_type=AddInput,
            config=None,
            execute=execute_tool,
        )

        tool_config = ToolConfig(
            tool_loop_policy=ToolLoopPolicyMaxSteps(
                max_steps=1,
            ),
            tools=[tool],
        )

        model = TestModel(
            call_tools=["add"],
        )

        agent, usage_limits = create_pydantic_ai_agent(
            model,
            tool_config,
        )

        result = await agent.run(
            "Add 1 and 2.",
            usage_limits=usage_limits,
        )

        execute.assert_awaited_once()

        assert execute.await_args is not None
        input_value = execute.await_args.args[0]

        assert input_value == AddInput(
            left=0,
            right=0,
        )

        assert execute.await_args.args[1] is None
        assert result.output is not None

    @pytest.mark.asyncio
    async def test_tool_returns_failure_result(self) -> None:
        execute = AsyncMock(
            return_value=ToolFailureResult(
                error=PublicError(
                    code="FILE_NOT_FOUND",
                    message="The requested file was not found.",
                    retryable=False,
                ),
            ),
        )

        async def execute_tool(
            input: AddInput,
            config: TestToolConfig | None,
        ) -> ToolResult[int]:
            return await execute(input, config)

        tool = AiTool(
            name="add",
            description="Add two numbers.",
            input_type=AddInput,
            config=None,
            execute=execute_tool,
        )

        tool_config = ToolConfig(
            tool_loop_policy=ToolLoopPolicyMaxSteps(
                max_steps=1,
            ),
            tools=[tool],
        )

        model = TestModel(
            call_tools=["add"],
        )

        agent, usage_limits = create_pydantic_ai_agent(
            model,
            tool_config,
        )

        result = await agent.run(
            "Add 1 and 2.",
            usage_limits=usage_limits,
        )

        execute.assert_awaited_once()

        assert execute.await_args
        input_value = execute.await_args.args[0]

        assert input_value == AddInput(
            left=0,
            right=0,
        )

        assert execute.await_args.args[1] is None

        assert result.output is not None
