from unittest.mock import AsyncMock

import pytest
from gyomu_ai.execution.parameter import GenerateObjectParams
from gyomu_ai.model.ai_model import AiModelKey
from gyomu_ai.provider.pydantic_ai.route_service import PydanticAiRoutingExecution
from gyomu_ai_compiler.pipelines.document.executor.object import build_section_object
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


class TestBuildSectionObject:
    @pytest.fixture
    def context(self) -> UserTest:
        return UserTest(user_id="uid", name="Alice")

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
            "gyomu_ai_compiler.pipelines.document.executor.object"
            ".PydanticAiRoutingExecution",
        )
        execution.generate_object = AsyncMock()

        result = await build_section_object(
            "test-section",
            context,
            provider,
            UserTest,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error
        render.assert_called_once_with("test-section", context)
        execution.generate_object.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_returns_ai_failure(
        self,
        mocker: MockerFixture,
        context: UserTest,
    ) -> None:
        conversation = mocker.sentinel.conversation
        render = mocker.Mock(return_value=Success(conversation))
        provider = SectionPromptProvider(render=render)

        ai_error = AiError(
            "Failed to generate object.",
            operation=AiOperation.GENERATE,
            model_key=AiModelKey.FAST,
            model=None,
            phase=AiErrorPhase.REQUEST,
            resolution=AiFailResolution(),
        )

        execution = mocker.Mock(spec=PydanticAiRoutingExecution)
        execution.generate_object = AsyncMock(
            return_value=Failure(ai_error),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.document.executor.object"
            ".PydanticAiRoutingExecution",
            return_value=execution,
        )

        result = await build_section_object(
            "test-section",
            context,
            provider,
            UserTest,
        )

        assert isinstance(result, Failure)
        assert result.failure() is ai_error
        execution.generate_object.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_returns_generated_object(
        self,
        mocker: MockerFixture,
        context: UserTest,
    ) -> None:
        conversation = mocker.sentinel.conversation
        render = mocker.Mock(return_value=Success(conversation))
        provider = SectionPromptProvider(render=render)

        output = UserTest(
            user_id="generated-uid",
            name="Bob",
        )

        response = mocker.Mock()
        response.output = output

        execution = mocker.Mock(spec=PydanticAiRoutingExecution)
        execution.generate_object = AsyncMock(
            return_value=Success(response),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.document.executor.object"
            ".PydanticAiRoutingExecution",
            return_value=execution,
        )

        result = await build_section_object(
            "test-section",
            context,
            provider,
            UserTest,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is output

    @pytest.mark.asyncio
    async def test_passes_section_id_context_conversation_and_schema_to_execution(
        self,
        mocker: MockerFixture,
        context: UserTest,
    ) -> None:
        conversation = mocker.sentinel.conversation
        render = mocker.Mock(return_value=Success(conversation))
        provider = SectionPromptProvider(render=render)

        output = UserTest(
            user_id="generated-uid",
            name="Bob",
        )

        response = mocker.Mock()
        response.output = output

        execution = mocker.Mock(spec=PydanticAiRoutingExecution)
        execution.generate_object = AsyncMock(
            return_value=Success(response),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.document.executor.object"
            ".PydanticAiRoutingExecution",
            return_value=execution,
        )

        section_id = "test-section"

        await build_section_object(
            section_id,
            context,
            provider,
            UserTest,
        )

        render.assert_called_once_with(section_id, context)

        execution.generate_object.assert_awaited_once()

        assert execution.generate_object.await_args
        conversation_arg = execution.generate_object.await_args.kwargs["conversation"]
        params = execution.generate_object.await_args.kwargs["params"]

        assert conversation_arg is conversation
        assert isinstance(params, GenerateObjectParams)
        assert params.key is AiModelKey.FAST
        assert params.output_type is UserTest
