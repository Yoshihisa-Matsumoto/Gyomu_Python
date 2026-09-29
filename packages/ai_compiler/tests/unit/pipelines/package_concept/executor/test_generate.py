from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from gyomu_ai.execution.parameter import GenerateObjectParams
from gyomu_ai.model.ai_model import AiModelKey
from gyomu_ai.provider.pydantic_ai.route_service import PydanticAiRoutingExecution
from gyomu_ai_compiler.pipelines.package_concept.executor.generate import (
    generate_package_concept,
)
from gyomu_schema.error.ai import (
    AiError,
    AiErrorPhase,
    AiFailResolution,
    AiOperation,
)
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.schemas.concept.package.analysis import PackageAnalysis
from gyomu_schema.schemas.concept.package.concept import PackageConcept
from gyomu_schema.schemas.python.types import ProjectRelativePath
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.schema.schema_test_support.concept_helpers import (
    create_capability_concept,
    create_dependency_analysis,
    create_dependency_summary,
    create_directory_analysis,
    create_directory_analysis_fact,
    create_directory_concept,
    create_file_summary,
    create_package_analysis,
    create_package_concept,
    create_public_declaration_summary,
    create_pyproject_analysis,
)


class TestGeneratePackageConcept:
    @pytest.fixture
    def context(self) -> PackageAnalysis:
        return create_package_analysis(
            package=create_pyproject_analysis(),
            dependencies=tuple([create_dependency_analysis()]),
            directories=tuple(
                [
                    create_directory_analysis(
                        path=ProjectRelativePath(Path("src")),
                        concept=create_directory_concept(),
                        fact=create_directory_analysis_fact(),
                    ),
                ]
            ),
            public_files=tuple(
                [
                    create_file_summary(
                        path=ProjectRelativePath(Path("src/test.py")),
                        exports=tuple(
                            [
                                create_public_declaration_summary(),
                            ]
                        ),
                        dependencies=tuple([create_dependency_summary()]),
                    )
                ]
            ),
        )

    @pytest.fixture
    def concept(self) -> PackageConcept:
        return create_package_concept(
            summary="Example directory.",
            responsibilities=["Provide example functionality."],
            capabilities=[create_capability_concept()],
            usage_guidance=["usage guidance"],
            design_decisions=["design decision"],
        )

    @pytest.mark.asyncio
    async def test_returns_prompt_loading_failure(
        self,
        mocker: MockerFixture,
        context: PackageAnalysis,
    ) -> None:
        error = GyomuIOError(
            "Failed to load prompt.",
            layer=IOLayer.FILESYSTEM,
            operation=IOOperation.READ,
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.package_concept.executor.generate.load_prompt",
            return_value=Failure(error),
        )

        execution = mocker.patch(
            "gyomu_ai_compiler.pipelines.package_concept.executor.generate"
            ".PydanticAiRoutingExecution",
        )

        result = await generate_package_concept(context)

        assert isinstance(result, Failure)
        assert result.failure() is error
        execution.assert_not_called()

    @pytest.mark.asyncio
    async def test_returns_ai_failure(
        self,
        mocker: MockerFixture,
        context: PackageAnalysis,
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
            "gyomu_ai_compiler.pipelines.package_concept.executor.generate.load_prompt",
            return_value=Success("system prompt"),
        )
        mocker.patch(
            "gyomu_ai_compiler.pipelines.package_concept.executor.generate.render_package_analysis",
            return_value="",
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.package_concept.executor.generate"
            ".PydanticAiRoutingExecution",
            return_value=execution,
        )

        result = await generate_package_concept(context)

        assert isinstance(result, Failure)
        assert result.failure() is ai_error
        execution.generate_object.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_returns_generated_concept(
        self,
        mocker: MockerFixture,
        context: PackageAnalysis,
        concept: PackageConcept,
    ) -> None:
        response = mocker.Mock()
        response.output = concept

        execution = mocker.Mock(spec=PydanticAiRoutingExecution)
        execution.generate_object = AsyncMock(
            return_value=Success(response),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.package_concept.executor.generate.load_prompt",
            return_value=Success("system prompt"),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.package_concept.executor.generate"
            ".PydanticAiRoutingExecution",
            return_value=execution,
        )

        result = await generate_package_concept(context)

        assert isinstance(result, Success)
        assert result.unwrap() is concept

    @pytest.mark.asyncio
    async def test_passes_rendered_prompt_to_execution(
        self,
        mocker: MockerFixture,
        context: PackageAnalysis,
        concept: PackageConcept,
    ) -> None:
        response = mocker.Mock()
        response.output = concept

        execution = mocker.Mock(spec=PydanticAiRoutingExecution)
        execution.generate_object = AsyncMock(
            return_value=Success(response),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.package_concept.executor.generate.load_prompt",
            return_value=Success("Before\n<##PACKAGE##>\nAfter"),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.package_concept.executor.generate"
            ".PydanticAiRoutingExecution",
            return_value=execution,
        )

        render_package_analysis = mocker.patch(
            "gyomu_ai_compiler.pipelines.package_concept.executor.generate"
            ".render_package_analysis",
            return_value="test",
        )

        await generate_package_concept(context)

        execution.generate_object.assert_awaited_once()

        assert execution.generate_object.await_args
        conversation, params = execution.generate_object.await_args.args

        assert conversation.request is not None
        assert conversation.request.parts[0].text == "Before\ntest\nAfter"

        render_package_analysis.assert_called_once_with(context)

        assert isinstance(params, GenerateObjectParams)
        assert params.key is AiModelKey.FAST
        assert params.output_type is PackageConcept
