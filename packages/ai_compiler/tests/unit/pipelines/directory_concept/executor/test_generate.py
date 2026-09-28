from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from gyomu_ai.execution.parameter import GenerateObjectParams
from gyomu_ai.model.ai_model import AiModelKey
from gyomu_ai.provider.pydantic_ai.route_service import PydanticAiRoutingExecution
from gyomu_ai_compiler.pipelines.directory_concept.executor.generate import (
    generate_directory_concept,
)
from gyomu_schema.error.ai import (
    AiError,
    AiErrorPhase,
    AiFailResolution,
    AiOperation,
)
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.schemas.concept.directory.concept import (
    DirectoryConcept,
    DirectoryImportance,
)
from gyomu_schema.schemas.concept.directory.input import DirectoryConceptInput
from gyomu_schema.schemas.concept.file_summary import (
    DependencySummary,
)
from gyomu_schema.schemas.python.symbol_base import DeclarationKind
from gyomu_schema.schemas.python.types import ProjectRelativePath
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.schema.schema_test_support.concept_helpers import (
    create_directory_concept,
    create_directory_concept_input,
    create_file_summary,
    create_public_declaration_summary,
    create_sub_directory_input,
)


class TestGenerateDirectoryConcept:
    @pytest.fixture
    def context(self) -> DirectoryConceptInput:
        file_summary = create_file_summary(
            path=ProjectRelativePath(Path("src/example.py")),
            exports=(
                create_public_declaration_summary(
                    symbol="example::Example",
                    kind=DeclarationKind.CLASS,
                    summary="Example class.",
                ),
            ),
            dependencies=(
                DependencySummary(
                    target="example::Dependency",
                    external=False,
                ),
            ),
        )

        sub_directory = create_sub_directory_input(
            path=Path("internal"),
            concept=create_directory_concept(
                summary="Internal implementation.",
                responsibilities=["Provide internal implementation."],
                concepts=["Internal implementation"],
                relationships=[],
                design_decisions=[],
                importance=DirectoryImportance.SUPPORTING,
            ),
        )

        return create_directory_concept_input(
            files=(file_summary,),
            sub_directories=(sub_directory,),
        )

    @pytest.fixture
    def concept(self) -> DirectoryConcept:
        return create_directory_concept(
            summary="Example directory.",
            responsibilities=["Provide example functionality."],
            concepts=["Example"],
            relationships=["Example depends on its internal implementation."],
            design_decisions=["Keep the directory focused on example functionality."],
            importance=DirectoryImportance.CORE,
        )

    @pytest.mark.asyncio
    async def test_returns_prompt_loading_failure(
        self,
        mocker: MockerFixture,
        context: DirectoryConceptInput,
    ) -> None:
        error = GyomuIOError(
            "Failed to load prompt.",
            layer=IOLayer.FILESYSTEM,
            operation=IOOperation.READ,
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.directory_concept.executor.generate"
            ".load_prompt",
            return_value=Failure(error),
        )

        execution = mocker.patch(
            "gyomu_ai_compiler.pipelines.directory_concept.executor.generate"
            ".PydanticAiRoutingExecution",
        )

        result = await generate_directory_concept(context)

        assert isinstance(result, Failure)
        assert result.failure() is error
        execution.assert_not_called()

    @pytest.mark.asyncio
    async def test_returns_ai_failure(
        self,
        mocker: MockerFixture,
        context: DirectoryConceptInput,
    ) -> None:
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
            "gyomu_ai_compiler.pipelines.directory_concept.executor.generate"
            ".load_prompt",
            return_value=Success("system prompt"),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.directory_concept.executor.generate"
            ".PydanticAiRoutingExecution",
            return_value=execution,
        )

        result = await generate_directory_concept(context)

        assert isinstance(result, Failure)
        assert result.failure() is ai_error
        execution.generate_object.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_returns_generated_concept(
        self,
        mocker: MockerFixture,
        context: DirectoryConceptInput,
        concept: DirectoryConcept,
    ) -> None:
        response = mocker.Mock()
        response.output = concept

        execution = mocker.Mock(spec=PydanticAiRoutingExecution)
        execution.generate_object = AsyncMock(
            return_value=Success(response),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.directory_concept.executor.generate"
            ".load_prompt",
            return_value=Success("system prompt"),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.directory_concept.executor.generate"
            ".PydanticAiRoutingExecution",
            return_value=execution,
        )

        result = await generate_directory_concept(context)

        assert isinstance(result, Success)
        assert result.unwrap() is concept

    @pytest.mark.asyncio
    async def test_passes_rendered_prompt_to_execution(
        self,
        mocker: MockerFixture,
        context: DirectoryConceptInput,
        concept: DirectoryConcept,
    ) -> None:
        response = mocker.Mock()
        response.output = concept

        execution = mocker.Mock(spec=PydanticAiRoutingExecution)
        execution.generate_object = AsyncMock(
            return_value=Success(response),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.directory_concept.executor.generate"
            ".load_prompt",
            return_value=Success(
                "Before\n<##FILES##>\nMiddle\n<##DIRECTORIES##>\nAfter"
            ),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.directory_concept.executor.generate"
            ".PydanticAiRoutingExecution",
            return_value=execution,
        )

        render_file_summary = mocker.patch(
            "gyomu_ai_compiler.pipelines.directory_concept.executor.generate"
            ".render_file_summary",
            side_effect=lambda file: f"FILE:{file.path}",
        )
        render_sub_directory = mocker.patch(
            "gyomu_ai_compiler.pipelines.directory_concept.executor.generate"
            ".render_sub_directory",
            side_effect=lambda directory: f"DIRECTORY:{directory.path}",
        )

        await generate_directory_concept(context)

        execution.generate_object.assert_awaited_once()

        assert execution.generate_object.await_args
        conversation, params = execution.generate_object.await_args.args

        assert conversation.request is not None
        assert (
            conversation.request.parts[0].text == "Before\n"
            "FILE:src/example.py\n"
            "Middle\n"
            "DIRECTORY:internal\n"
            "After"
        )

        render_file_summary.assert_called_once_with(context.files[0])
        render_sub_directory.assert_called_once_with(context.sub_directories[0])

        assert isinstance(params, GenerateObjectParams)
        assert params.key is AiModelKey.FAST
        assert params.output_type is DirectoryConcept
