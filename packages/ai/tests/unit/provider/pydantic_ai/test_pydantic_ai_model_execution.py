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
)
from gyomu_ai.execution.result import (
    AiEmbeddingResult,
    AiGenerateObjectResult,
    AiGenerateTextResult,
)
from gyomu_ai.model.ai_model import AiModelKey
from gyomu_ai.provider.pydantic_ai.ai_model import PydanticAiModelRegistry
from gyomu_ai.provider.pydantic_ai.execution import PydanticAiModelExecution
from gyomu_ai.provider.pydantic_ai.result import PydanticAiTextStream
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import MessageSchema
from pydantic import BaseModel
from pydantic_ai.models import Model
from returns.result import Success


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

        agent_class = MagicMock(return_value=agent)

        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.Agent",
            agent_class,
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

        agent_class.assert_called_once_with(model=model)

        agent.run.assert_awaited_once_with(
            instructions=prompt.instructions,
            user_prompt=prompt.user_prompt,
            message_history=prompt.message_history,
            model_settings=model_settings,
        )

        assert isinstance(
            result.unwrap(),
            AiGenerateTextResult,
        )


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

        agent_class = MagicMock(return_value=agent)

        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.Agent",
            agent_class,
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

        agent_class.assert_called_once_with(
            model=model,
            output_type=DummyOutput,
        )

        agent.run.assert_awaited_once()


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

        agent_class = MagicMock(return_value=agent)

        monkeypatch.setattr(
            "gyomu_ai.provider.pydantic_ai.execution.Agent",
            agent_class,
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

        agent_class.assert_called_once_with(model=model)

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
