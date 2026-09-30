from pathlib import Path

import pytest
from gyomu_facts.package.analysis import (
    ImportanceDirectorySelection,
    PackageFacts,
    TopScoreDirectorySelection,
)
from gyomu_schema.schemas.concept.directory.concept import DirectoryImportance
from gyomu_schema.schemas.concept.package.analysis import (
    DirectoryAnalysis,
    PackageAnalysis,
)
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


class TestPackageFacts:
    @pytest.fixture
    def directories(self) -> tuple[DirectoryAnalysis, ...]:
        return (
            create_directory_analysis(
                path=ProjectRelativePath(Path("core")),
                concept=create_directory_concept(
                    importance=DirectoryImportance.CORE,
                ),
                fact=create_directory_analysis_fact(
                    public_symbol_count=10,
                ),
            ),
            create_directory_analysis(
                path=ProjectRelativePath(Path("supporting")),
                concept=create_directory_concept(
                    importance=DirectoryImportance.SUPPORTING,
                ),
                fact=create_directory_analysis_fact(
                    public_symbol_count=5,
                ),
            ),
            create_directory_analysis(
                path=ProjectRelativePath(Path("utility")),
                concept=create_directory_concept(
                    importance=DirectoryImportance.UTILITY,
                ),
                fact=create_directory_analysis_fact(
                    public_symbol_count=2,
                ),
            ),
        )

    @pytest.fixture
    def analysis(self, directories) -> PackageAnalysis:
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
            directories=directories,
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

    def test_returns_all_ranked_directories_for_top_score_without_limit(
        self,
        mocker: MockerFixture,
        analysis: PackageAnalysis,
        directories: tuple[DirectoryAnalysis, ...],
    ) -> None:
        ranked = (
            directories[2],
            directories[1],
            directories[0],
        )

        rank = mocker.patch(
            "gyomu_facts.package.analysis.rank_directories_by_score",
            return_value=ranked,
        )

        facts = PackageFacts(analysis)

        result = facts.get_ranked_directories(TopScoreDirectorySelection(limit=None))

        assert result == ranked
        rank.assert_called_once_with(analysis.directories)

    def test_limits_top_score_directories(
        self,
        mocker: MockerFixture,
        analysis: PackageAnalysis,
        directories: tuple[DirectoryAnalysis, ...],
    ) -> None:
        ranked = (
            directories[2],
            directories[1],
            directories[0],
        )

        mocker.patch(
            "gyomu_facts.package.analysis.rank_directories_by_score",
            return_value=ranked,
        )

        facts = PackageFacts(analysis)

        result = facts.get_ranked_directories(TopScoreDirectorySelection(limit=2))

        assert result == (
            directories[2],
            directories[1],
        )

    def test_selects_directories_by_importance(
        self,
        analysis: PackageAnalysis,
        directories: tuple[DirectoryAnalysis, ...],
    ) -> None:
        facts = PackageFacts(analysis)

        result = facts.get_ranked_directories(
            ImportanceDirectorySelection(
                limits={
                    DirectoryImportance.CORE: 1,
                    DirectoryImportance.SUPPORTING: 1,
                    DirectoryImportance.UTILITY: 1,
                }
            )
        )

        assert result == directories

    def test_limits_each_importance(
        self,
    ) -> None:
        core1 = create_directory_analysis(
            path=ProjectRelativePath(Path("core1")),
            concept=create_directory_concept(
                importance=DirectoryImportance.CORE,
            ),
            fact=create_directory_analysis_fact(),
        )
        core2 = create_directory_analysis(
            path=ProjectRelativePath(Path("core2")),
            concept=create_directory_concept(
                importance=DirectoryImportance.CORE,
            ),
            fact=create_directory_analysis_fact(),
        )
        utility = create_directory_analysis(
            path=ProjectRelativePath(Path("utility")),
            concept=create_directory_concept(
                importance=DirectoryImportance.UTILITY,
            ),
            fact=create_directory_analysis_fact(),
        )

        analysis = create_package_analysis(
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
            directories=(core1, core2, utility),
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

        facts = PackageFacts(analysis)

        result = facts.get_ranked_directories(
            ImportanceDirectorySelection(
                limits={
                    DirectoryImportance.CORE: 1,
                    DirectoryImportance.UTILITY: 1,
                }
            )
        )

        assert result == (
            core1,
            utility,
        )

    def test_preserves_importance_selection_order(
        self,
        analysis: PackageAnalysis,
        directories: tuple[DirectoryAnalysis, ...],
    ) -> None:
        facts = PackageFacts(analysis)

        result = facts.get_ranked_directories(
            ImportanceDirectorySelection(
                limits={
                    DirectoryImportance.UTILITY: 1,
                    DirectoryImportance.CORE: 1,
                }
            )
        )

        assert result == (
            directories[2],
            directories[0],
        )

    def test_returns_empty_for_empty_directories(self) -> None:
        analysis = create_package_analysis(
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
            directories=(),
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

        facts = PackageFacts(analysis)

        assert (
            facts.get_ranked_directories(TopScoreDirectorySelection(limit=None)) == ()
        )

        assert (
            facts.get_ranked_directories(
                ImportanceDirectorySelection(
                    limits={
                        DirectoryImportance.CORE: 1,
                        DirectoryImportance.SUPPORTING: 1,
                        DirectoryImportance.UTILITY: 1,
                    }
                )
            )
            == ()
        )
