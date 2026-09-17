from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from gyomu_ai.execution.parameter import GenerateObjectParams
from gyomu_ai.model.ai_model import AiModelKey
from gyomu_ai.provider.pydantic_ai.execution import PydanticAiModelExecution
from gyomu_ai_compiler.pipelines.docstring_update.context.file_context import (
    DocstringFileContext,
)
from gyomu_ai_compiler.pipelines.docstring_update.executor.update_plan import (
    generate_docstring_update_plan,
)
from gyomu_ai_compiler.pipelines.docstring_update.schema.ai_plan import (
    DocstringUpdatePlan,
)
from gyomu_schema.error.ai import (
    AiError,
    AiErrorPhase,
    AiFailResolution,
    AiOperation,
)
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.option.retry import RetryOption
from gyomu_schema.schemas.python.types import SourceRelativePath
from pytest_mock import MockerFixture
from returns.result import Failure, Success


class TestGenerateDocstringUpdatePlan:
    @pytest.fixture
    def context(self) -> DocstringFileContext:
        return DocstringFileContext(
            project_name="test-project",
            source_relative_path=SourceRelativePath(Path("src/example.py")),
            symbols=(),
            retry=None,
        )

    @pytest.fixture
    def plan(self) -> DocstringUpdatePlan:
        return DocstringUpdatePlan(
            entries=(),
        )

    @pytest.mark.asyncio
    async def test_returns_prompt_loading_failure(
        self,
        mocker: MockerFixture,
        context: DocstringFileContext,
    ) -> None:
        error = GyomuIOError(
            "Failed to load prompt.",
            layer=IOLayer.FILESYSTEM,
            operation=IOOperation.READ,
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.docstring_update.executor.update_plan"
            ".load_docstring_update_base_prompt",
            return_value=Failure(error),
        )

        execution = mocker.patch(
            "gyomu_ai_compiler.pipelines.docstring_update.executor.update_plan"
            ".PydanticAiModelExecution",
        )

        result = await generate_docstring_update_plan(context)

        assert isinstance(result, Failure)
        assert result.failure() is error
        execution.assert_not_called()

    @pytest.mark.asyncio
    async def test_returns_ai_error_when_registry_creation_fails(
        self,
        mocker: MockerFixture,
        context: DocstringFileContext,
    ) -> None:
        exception = RuntimeError("GEMINI_API_KEY is not configured.")

        mocker.patch(
            "gyomu_ai_compiler.pipelines.docstring_update.executor.update_plan"
            ".load_docstring_update_base_prompt",
            return_value=Success("system prompt"),
        )
        mocker.patch(
            "gyomu_ai_compiler.pipelines.docstring_update.executor.update_plan"
            ".create_default_pydantic_ai_model_registry",
            side_effect=exception,
        )

        result = await generate_docstring_update_plan(context)

        assert isinstance(result, Failure)

        error = result.failure()
        assert isinstance(error, AiError)
        assert error.operation is AiOperation.GENERATE
        assert error.model_key is None
        assert error.model is None
        assert error.phase is AiErrorPhase.REQUEST
        assert error.resolution == AiFailResolution()

    @pytest.mark.asyncio
    async def test_returns_ai_failure(
        self,
        mocker: MockerFixture,
        context: DocstringFileContext,
    ) -> None:
        ai_error = AiError(
            "Failed to generate object.",
            operation=AiOperation.GENERATE,
            model_key=AiModelKey.FAST,
            model=None,
            phase=AiErrorPhase.REQUEST,
            resolution=AiFailResolution(),
        )

        execution = mocker.Mock(spec=PydanticAiModelExecution)
        execution.generate_object = AsyncMock(
            return_value=Failure(ai_error),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.docstring_update.executor.update_plan"
            ".load_docstring_update_base_prompt",
            return_value=Success("system prompt"),
        )
        mocker.patch(
            "gyomu_ai_compiler.pipelines.docstring_update.executor.update_plan"
            ".create_default_pydantic_ai_model_registry",
            return_value=mocker.sentinel.registry,
        )
        mocker.patch(
            "gyomu_ai_compiler.pipelines.docstring_update.executor.update_plan"
            ".PydanticAiModelExecution",
            return_value=execution,
        )

        result = await generate_docstring_update_plan(context)

        assert isinstance(result, Failure)
        assert result.failure() is ai_error
        execution.generate_object.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_returns_generated_plan(
        self,
        mocker: MockerFixture,
        context: DocstringFileContext,
        plan: DocstringUpdatePlan,
    ) -> None:
        response = mocker.Mock()
        response.output = plan

        execution = mocker.Mock(spec=PydanticAiModelExecution)
        execution.generate_object = AsyncMock(
            return_value=Success(response),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.docstring_update.executor.update_plan"
            ".load_docstring_update_base_prompt",
            return_value=Success("system prompt"),
        )
        mocker.patch(
            "gyomu_ai_compiler.pipelines.docstring_update.executor.update_plan"
            ".create_default_pydantic_ai_model_registry",
            return_value=mocker.sentinel.registry,
        )
        mocker.patch(
            "gyomu_ai_compiler.pipelines.docstring_update.executor.update_plan"
            ".PydanticAiModelExecution",
            return_value=execution,
        )

        result = await generate_docstring_update_plan(context)

        assert isinstance(result, Success)
        assert result.unwrap() is plan

    @pytest.mark.asyncio
    async def test_passes_prompt_and_context_to_execution(
        self,
        mocker: MockerFixture,
        context: DocstringFileContext,
        plan: DocstringUpdatePlan,
    ) -> None:
        response = mocker.Mock()
        response.output = plan

        execution = mocker.Mock(spec=PydanticAiModelExecution)
        execution.generate_object = AsyncMock(
            return_value=Success(response),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.docstring_update.executor.update_plan"
            ".load_docstring_update_base_prompt",
            return_value=Success("system prompt"),
        )
        mocker.patch(
            "gyomu_ai_compiler.pipelines.docstring_update.executor.update_plan"
            ".create_default_pydantic_ai_model_registry",
            return_value=mocker.sentinel.registry,
        )
        mocker.patch(
            "gyomu_ai_compiler.pipelines.docstring_update.executor.update_plan"
            ".PydanticAiModelExecution",
            return_value=execution,
        )
        serialized_context = '{"project_name": "test"}'

        dump_json = mocker.patch(
            "gyomu_ai_compiler.pipelines.docstring_update.executor.update_plan.dump_json",
            return_value=serialized_context,
        )

        await generate_docstring_update_plan(context)

        execution.generate_object.assert_awaited_once()

        assert execution.generate_object.await_args
        conversation, params = execution.generate_object.await_args.args

        assert conversation.system is not None
        assert conversation.system.parts[0].text == "system prompt"

        assert conversation.request is not None
        # assert conversation.request.content == context.model_dump_json(indent=2)
        dump_json.assert_called_once_with(context, indent=2)
        assert conversation.request.parts[0].text == serialized_context

        assert isinstance(params, GenerateObjectParams)
        assert params.key is AiModelKey.FAST
        assert params.output_type is DocstringUpdatePlan

    @pytest.mark.asyncio
    async def test_passes_ai_retry_option(
        self,
        mocker: MockerFixture,
        context: DocstringFileContext,
        plan: DocstringUpdatePlan,
    ) -> None:
        response = mocker.Mock()
        response.output = plan

        execution = mocker.Mock(spec=PydanticAiModelExecution)
        execution.generate_object = AsyncMock(
            return_value=Success(response),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.docstring_update.executor.update_plan"
            ".load_docstring_update_base_prompt",
            return_value=Success("system prompt"),
        )
        mocker.patch(
            "gyomu_ai_compiler.pipelines.docstring_update.executor.update_plan"
            ".create_default_pydantic_ai_model_registry",
            return_value=mocker.sentinel.registry,
        )
        mocker.patch(
            "gyomu_ai_compiler.pipelines.docstring_update.executor.update_plan"
            ".PydanticAiModelExecution",
            return_value=execution,
        )

        retry_option = RetryOption(max_attempts=3, observer=None)

        await generate_docstring_update_plan(
            context,
            retry_option=retry_option,
        )

        assert execution.generate_object.await_args
        _, params = execution.generate_object.await_args.args

        assert isinstance(params, GenerateObjectParams)
        assert params.execution is not None
        assert params.execution.retry_option is retry_option
