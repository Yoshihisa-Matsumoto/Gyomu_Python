from pathlib import Path

import pytest
from gyomu_concept.error.concept import ConceptError
from gyomu_concept.package.concept import build_package_concept
from gyomu_infra.logger import logger
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.package.analysis import PackageAnalysis
from gyomu_schema.schemas.concept.package.concept import PackageConcept
from gyomu_schema.schemas.python.types import ProjectRelativePath
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.concept.concept_test_support.helpers import (
    _create_directory_project_context,
)
from packages.schema.schema_test_support.concept_helpers import (
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


class TestBuildPackageConcept:
    @pytest.fixture
    def context(self) -> ProjectContext:
        return _create_directory_project_context()

    @pytest.fixture
    def analysis(self) -> PackageAnalysis:
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
            capabilities=[],
            usage_guidance=["usage guidance"],
            design_decisions=["design decision"],
        )

    @pytest.mark.asyncio
    async def test_returns_generated_concept(
        self,
        mocker: MockerFixture,
        context: ProjectContext,
        analysis: PackageAnalysis,
        concept: PackageConcept,
    ) -> None:
        build_analysis = mocker.patch(
            "gyomu_concept.package.concept.build_package_analysis",
            return_value=Success(analysis),
        )
        process = mocker.patch(
            "gyomu_concept.package.concept.process_package_concept",
            return_value=Success(concept),
        )
        save = mocker.patch(
            "gyomu_concept.package.concept.save_package_concept",
            return_value=Success(None),
        )

        result = await build_package_concept(context=context)

        assert isinstance(result, Success)
        assert result.unwrap() is concept

        build_analysis.assert_called_once_with(context, None)
        process.assert_called_once_with(
            package_name=context.config.name,
            package_path=context.source_root,
            context=analysis,
        )
        save.assert_called_once_with(
            context=context,
            concept=concept,
            option=None,
        )

    @pytest.mark.asyncio
    async def test_returns_failure_when_build_analysis_fails(
        self,
        mocker: MockerFixture,
        context: ProjectContext,
    ) -> None:
        error = ConceptError(
            message="failed to build analysis",
            file_path=context.project_root,
            package_name=context.config.name,
            phase="package-concept",
            identity=None,
        )

        build_analysis = mocker.patch(
            "gyomu_concept.package.concept.build_package_analysis",
            return_value=Failure(error),
        )
        process = mocker.patch(
            "gyomu_concept.package.concept.process_package_concept",
        )
        save = mocker.patch(
            "gyomu_concept.package.concept.save_package_concept",
        )

        result = await build_package_concept(context=context)

        assert isinstance(result, Failure)
        assert result.failure() is error

        build_analysis.assert_called_once_with(context, None)
        process.assert_not_called()
        save.assert_not_called()

    @pytest.mark.asyncio
    async def test_returns_failure_when_process_fails(
        self,
        mocker: MockerFixture,
        context: ProjectContext,
        analysis: PackageAnalysis,
    ) -> None:
        error = ConceptError(
            message="failed to generate concept",
            file_path=context.source_root,
            package_name=context.config.name,
            phase="package-concept",
            identity=None,
        )

        mocker.patch(
            "gyomu_concept.package.concept.build_package_analysis",
            return_value=Success(analysis),
        )
        process = mocker.patch(
            "gyomu_concept.package.concept.process_package_concept",
            return_value=Failure(error),
        )
        save = mocker.patch(
            "gyomu_concept.package.concept.save_package_concept",
        )

        result = await build_package_concept(context=context)

        assert isinstance(result, Failure)
        assert result.failure() is error

        process.assert_called_once_with(
            package_name=context.config.name,
            package_path=context.source_root,
            context=analysis,
        )
        save.assert_not_called()

    @pytest.mark.asyncio
    async def test_returns_failure_when_save_fails(
        self,
        mocker: MockerFixture,
        context: ProjectContext,
        analysis: PackageAnalysis,
        concept: PackageConcept,
    ) -> None:
        error = ConceptError(
            message="failed to save concept",
            file_path=context.project_root,
            package_name=context.config.name,
            phase="package-concept",
            identity=None,
        )

        mocker.patch(
            "gyomu_concept.package.concept.build_package_analysis",
            return_value=Success(analysis),
        )
        mocker.patch(
            "gyomu_concept.package.concept.process_package_concept",
            return_value=Success(concept),
        )
        save = mocker.patch(
            "gyomu_concept.package.concept.save_package_concept",
            return_value=Failure(error),
        )

        result = await build_package_concept(context=context)

        assert isinstance(result, Failure)
        assert result.failure() is error

        save.assert_called_once_with(
            context=context,
            concept=concept,
            option=None,
        )

    @pytest.mark.asyncio
    async def test_returns_existing_concept_when_no_files_changed(
        self,
        mocker: MockerFixture,
        context: ProjectContext,
        concept: PackageConcept,
    ) -> None:
        option = ConceptOption(changed_files=tuple([]))

        load = mocker.patch(
            "gyomu_concept.package.concept.load_package_concept",
            return_value=Success(concept),
        )
        build_analysis = mocker.patch(
            "gyomu_concept.package.concept.build_package_analysis",
        )
        process = mocker.patch(
            "gyomu_concept.package.concept.process_package_concept",
        )
        save = mocker.patch(
            "gyomu_concept.package.concept.save_package_concept",
        )

        result = await build_package_concept(
            context=context,
            option=option,
        )
        if isinstance(result, Failure):
            logger.debug_object(result.failure())
        assert isinstance(result, Success)
        assert result.unwrap() is concept

        load.assert_called_once_with(context, option)
        build_analysis.assert_not_called()
        process.assert_not_called()
        save.assert_not_called()

    @pytest.mark.asyncio
    async def test_builds_concept_when_no_files_changed_but_concept_does_not_exist(
        self,
        mocker: MockerFixture,
        context: ProjectContext,
        analysis: PackageAnalysis,
        concept: PackageConcept,
    ) -> None:
        option = ConceptOption(changed_files=tuple([]))

        load = mocker.patch(
            "gyomu_concept.package.concept.load_package_concept",
            return_value=Success(None),
        )
        build_analysis = mocker.patch(
            "gyomu_concept.package.concept.build_package_analysis",
            return_value=Success(analysis),
        )
        mocker.patch(
            "gyomu_concept.package.concept.process_package_concept",
            return_value=Success(concept),
        )
        save = mocker.patch(
            "gyomu_concept.package.concept.save_package_concept",
            return_value=Success(None),
        )

        result = await build_package_concept(
            context=context,
            option=option,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is concept

        load.assert_called_once_with(context, option)
        build_analysis.assert_called_once_with(context, option)
        save.assert_called_once_with(
            context=context,
            concept=concept,
            option=option,
        )
