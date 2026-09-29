from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from gyomu_concept.error.concept import ConceptError
from gyomu_concept.package.internal.process import process_package_concept
from gyomu_schema.error.ai import (
    AiError,
    AiErrorPhase,
    AiFailResolution,
    AiOperation,
)
from gyomu_schema.schemas.concept.package.analysis import PackageAnalysis
from gyomu_schema.schemas.concept.package.concept import PackageConcept
from gyomu_schema.schemas.python.types import ProjectRelativePath
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.schema.schema_test_support.concept_helpers import (
    create_capability_concept,
    create_dependency_analysis,
    create_directory_analysis,
    create_directory_analysis_fact,
    create_directory_concept,
    create_file_summary,
    create_package_analysis,
    create_package_concept,
    create_public_declaration_summary,
    create_pyproject_analysis,
)


class TestProcessPackageConcept:
    @pytest.fixture
    def package_name(self) -> str:
        return "test-package"

    @pytest.fixture
    def package_path(self) -> ProjectRelativePath:
        return ProjectRelativePath(Path("src/example"))

    @pytest.fixture
    def concept_input(self) -> PackageAnalysis:
        return create_package_analysis(
            package=create_pyproject_analysis(),
            dependencies=(
                create_dependency_analysis(
                    package_name="pydantic",
                    kind="version",
                    source="dependency",
                    required_version="<3,>=2",
                ),
                create_dependency_analysis(
                    package_name="pytest",
                    kind="version",
                    source="devDependency",
                    required_version=">=9",
                ),
            ),
            directories=(
                create_directory_analysis(
                    path=ProjectRelativePath(Path("src")),
                    concept=create_directory_concept(),
                    fact=create_directory_analysis_fact(),
                ),
            ),
            public_files=(
                create_file_summary(
                    path=ProjectRelativePath(Path("src/test.py")),
                    exports=(
                        create_public_declaration_summary(
                            symbol="test.module",
                            summary="Test symbol",
                        ),
                    ),
                    dependencies=(),
                ),
            ),
        )

    @pytest.fixture
    def concept(self) -> PackageConcept:
        return create_package_concept(
            summary="Example package.",
            responsibilities=["Provide example functionality."],
            capabilities=[create_capability_concept()],
            usage_guidance=["usage guidance"],
            design_decisions=["design decision"],
        )

    @pytest.mark.asyncio
    async def test_returns_generated_concept(
        self,
        mocker: MockerFixture,
        package_name: str,
        package_path: ProjectRelativePath,
        concept_input,
        concept,
    ) -> None:
        generate = mocker.patch(
            "gyomu_concept.package.internal.process.generate_package_concept",
            new_callable=AsyncMock,
            return_value=Success(concept),
        )

        result = await process_package_concept(
            package_name=package_name,
            package_path=package_path,
            context=concept_input,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is concept

        generate.assert_awaited_once_with(context=concept_input)

    @pytest.mark.asyncio
    async def test_returns_concept_error_on_failure(
        self,
        mocker: MockerFixture,
        package_name: str,
        package_path: ProjectRelativePath,
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
            "gyomu_concept.package.internal.process.generate_package_concept",
            new_callable=AsyncMock,
            return_value=Failure(ai_error),
        )

        result = await process_package_concept(
            package_name=package_name,
            package_path=package_path,
            context=concept_input,
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, ConceptError)
        assert error.message == "fail to generate Package Concept"
        assert error.file_path == package_path
        assert error.package_name == package_name
        assert error.phase == "package-concept"
        assert error.identity is None
        assert error.details == vars(concept_input)

        assert error.__cause__ is ai_error
