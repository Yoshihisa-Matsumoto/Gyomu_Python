from unittest.mock import AsyncMock

import pytest
from gyomu_ai.execution.parameter import GenerateTextParams
from gyomu_ai.model.ai_model import AiModelKey
from gyomu_ai.provider.pydantic_ai.route_service import PydanticAiRoutingExecution
from gyomu_ai_compiler.pipelines.document.executor.item import build_section_item
from gyomu_schema.error.ai import (
    AiError,
    AiErrorPhase,
    AiFailResolution,
    AiOperation,
)
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.schemas.document.section import SectionPromptProvider
from pydantic import BaseModel
from pytest_mock import MockerFixture
from returns.result import Failure, Success


class UserTest(BaseModel):
    user_id: str
    name: str


class TestBuildSectionItem:
    @pytest.fixture
    def context(self) -> UserTest:
        return UserTest(user_id="uid", name="Alice")

    @pytest.fixture
    def provider(
        self,
        mocker: MockerFixture,
    ) -> SectionPromptProvider[str, BaseModel]:
        return mocker.Mock(spec=SectionPromptProvider)

    @pytest.mark.asyncio
    async def test_returns_prompt_render_failure(
        self,
        mocker: MockerFixture,
        context: UserTest,
    ) -> None:
        error = GyomuIOError(
            "Failed to render prompt.",
            layer=IOLayer.FILESYSTEM,
            operation=IOOperation.READ,
        )
        render = mocker.Mock(
            return_value=Failure(error),
        )
        provider = SectionPromptProvider(render=render)

        execution = mocker.patch(
            "gyomu_ai_compiler.pipelines.document.executor.item"
            ".PydanticAiRoutingExecution",
        )
        execution.generate_text = AsyncMock()

        result = await build_section_item(
            "test-section",
            context,
            provider,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error
        render.assert_called_once_with("test-section", context)
        execution.generate_text.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_returns_ai_failure(
        self,
        mocker: MockerFixture,
        context: BaseModel,
    ) -> None:
        conversation = mocker.sentinel.conversation
        render = mocker.Mock(return_value=Success(conversation))
        provider = SectionPromptProvider(render=render)

        ai_error = AiError(
            "Failed to generate text.",
            operation=AiOperation.GENERATE,
            model_key=AiModelKey.FAST,
            model=None,
            phase=AiErrorPhase.REQUEST,
            resolution=AiFailResolution(),
        )

        execution = mocker.Mock(spec=PydanticAiRoutingExecution)
        execution.generate_text = AsyncMock(
            return_value=Failure(ai_error),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.document.executor.item"
            ".PydanticAiRoutingExecution",
            return_value=execution,
        )

        result = await build_section_item(
            "test-section",
            context,
            provider,
        )

        assert isinstance(result, Failure)
        assert result.failure() is ai_error
        execution.generate_text.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_returns_generated_text(
        self,
        mocker: MockerFixture,
        context: BaseModel,
        provider: SectionPromptProvider[str, BaseModel],
    ) -> None:
        conversation = mocker.sentinel.conversation
        render = mocker.Mock(return_value=Success(conversation))
        provider = SectionPromptProvider(render=render)

        response = mocker.Mock()
        response.message.text = "generated section text"

        execution = mocker.Mock(spec=PydanticAiRoutingExecution)
        execution.generate_text = AsyncMock(
            return_value=Success(response),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.document.executor.item"
            ".PydanticAiRoutingExecution",
            return_value=execution,
        )

        result = await build_section_item(
            "test-section",
            context,
            provider,
        )

        assert isinstance(result, Success)
        assert result.unwrap() == "generated section text"

    @pytest.mark.asyncio
    async def test_passes_section_id_context_and_conversation_to_execution(
        self,
        mocker: MockerFixture,
        context: BaseModel,
        provider: SectionPromptProvider[str, BaseModel],
    ) -> None:
        conversation = mocker.sentinel.conversation
        render = mocker.Mock(return_value=Success(conversation))
        provider = SectionPromptProvider(render=render)

        response = mocker.Mock()
        response.message.text = "generated section text"

        execution = mocker.Mock(spec=PydanticAiRoutingExecution)
        execution.generate_text = AsyncMock(
            return_value=Success(response),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.document.executor.item"
            ".PydanticAiRoutingExecution",
            return_value=execution,
        )

        section_id = "test-section"

        await build_section_item(
            section_id,
            context,
            provider,
        )

        render.assert_called_once_with(section_id, context)

        execution.generate_text.assert_awaited_once()

        assert execution.generate_text.await_args
        conversation_arg = execution.generate_text.await_args.kwargs["conversation"]
        params = execution.generate_text.await_args.kwargs["params"]

        assert conversation_arg is conversation
        assert isinstance(params, GenerateTextParams)
        assert params.key is AiModelKey.FAST
