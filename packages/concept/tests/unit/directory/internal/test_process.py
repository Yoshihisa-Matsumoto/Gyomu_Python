from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from gyomu_concept.directory.internal.process import process_directory_concept
from gyomu_concept.error.concept import ConceptError
from gyomu_schema.error.ai import (
    AiError,
    AiErrorPhase,
    AiFailResolution,
    AiOperation,
)
from gyomu_schema.schemas.concept.directory.concept import DirectoryImportance
from gyomu_schema.schemas.python.types import ProjectRelativePath
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.schema.schema_test_support.concept_helpers import (
    create_directory_concept,
    create_directory_concept_input,
)


class TestProcessDirectoryConcept:
    @pytest.fixture
    def package_name(self) -> str:
        return "test-package"

    @pytest.fixture
    def target_directory(self) -> ProjectRelativePath:
        return ProjectRelativePath(Path("src/example"))

    @pytest.fixture
    def concept_input(self):
        return create_directory_concept_input(
            files=(),
            sub_directories=(),
        )

    @pytest.fixture
    def concept(self):
        return create_directory_concept(
            summary="Example directory.",
            responsibilities=["Provide example functionality."],
            concepts=["Example"],
            relationships=[],
            design_decisions=[],
            importance=DirectoryImportance.CORE,
        )

    @pytest.mark.asyncio
    async def test_returns_generated_concept(
        self,
        mocker: MockerFixture,
        package_name: str,
        target_directory: ProjectRelativePath,
        concept_input,
        concept,
    ) -> None:
        generate = mocker.patch(
            "gyomu_concept.directory.internal.process.generate_directory_concept",
            new_callable=AsyncMock,
            return_value=Success(concept),
        )

        result = await process_directory_concept(
            package_name=package_name,
            target_directory=target_directory,
            concept=concept_input,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is concept

        generate.assert_awaited_once_with(context=concept_input)

    @pytest.mark.asyncio
    async def test_returns_concept_error_on_failure(
        self,
        mocker: MockerFixture,
        package_name: str,
        target_directory: ProjectRelativePath,
        concept_input,
    ) -> None:
        ai_error = AiError(
            "Failed to generate object.",
            operation=AiOperation.GENERATE,
            model_key="fast",
            model=None,
            phase=AiErrorPhase.REQUEST,
            resolution=AiFailResolution(),
        )

        mocker.patch(
            "gyomu_concept.directory.internal.process.generate_directory_concept",
            new_callable=AsyncMock,
            return_value=Failure(ai_error),
        )

        result = await process_directory_concept(
            package_name=package_name,
            target_directory=target_directory,
            concept=concept_input,
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, ConceptError)
        assert error.message == "fail to generate Directory Concept"
        assert error.file_path == target_directory
        assert error.package_name == package_name
        assert error.phase == "directory-summary"
        assert error.identity is None
        assert error.details == vars(concept_input)

        assert error.__cause__ is ai_error
