from pathlib import Path

import pytest
from gyomu_ai_compiler.pipelines.package_concept.context.input import (
    PackageDependencyInput,
    PublicApiSymbol,
    PublicSymbolsModule,
    TopDirectory,
)
from gyomu_ai_compiler.pipelines.package_concept.renderer.input import (
    build_package_concept_input,
)
from gyomu_facts.package.analysis import TopScoreDirectorySelection
from gyomu_schema.schemas.concept.package.analysis import PackageAnalysis
from gyomu_schema.schemas.python.types import ProjectRelativePath
from pytest_mock import MockerFixture

from packages.schema.schema_test_support.concept_helpers import (
    create_dependency_analysis,
    create_directory_analysis,
    create_directory_analysis_fact,
    create_directory_concept,
    create_file_summary,
    create_package_analysis,
    create_public_declaration_summary,
    create_pyproject_analysis,
)


class TestBuildPackageConceptInput:
    @pytest.fixture
    def context(self) -> PackageAnalysis:
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

    def test(self, context: PackageAnalysis) -> None:
        result = build_package_concept_input(context)

        assert result.package == context.package

        assert result.dependencies == (
            PackageDependencyInput(
                package_name="pydantic",
                version="<3,>=2",
            ),
        )

        assert result.public_symbols == (
            PublicSymbolsModule(
                module="test",
                symbols=(
                    PublicApiSymbol(
                        name="module",
                        summary="Test symbol",
                    ),
                ),
            ),
        )

    def test_top_directories(
        self,
        mocker: MockerFixture,
        context: PackageAnalysis,
    ) -> None:
        ranked = [
            mocker.Mock(
                path=ProjectRelativePath(Path("src/core")),
                concept=create_directory_concept(
                    summary="Core directory",
                    responsibilities=["Core responsibility"],
                ),
            ),
        ]

        get_ranked = mocker.patch(
            "gyomu_ai_compiler.pipelines.package_concept.renderer.input"
            ".PackageFacts.get_ranked_directories",
            return_value=ranked,
        )

        result = build_package_concept_input(context)

        assert result.top_directories == (
            TopDirectory(
                path=ProjectRelativePath(Path("src/core")),
                importance=ranked[0].concept.importance,
                responsibilities=("Core responsibility",),
                summary="Core directory",
            ),
        )

        get_ranked.assert_called_once_with(TopScoreDirectorySelection(limit=5))
