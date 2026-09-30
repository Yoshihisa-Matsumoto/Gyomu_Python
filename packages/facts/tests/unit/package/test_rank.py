from pathlib import Path

import pytest
from gyomu_facts.package.rank import calculate_score, rank_directories_by_score
from gyomu_schema.schemas.concept.directory.concept import DirectoryImportance
from gyomu_schema.schemas.python.types import ProjectRelativePath

from packages.schema.schema_test_support.concept_helpers import (
    create_directory_analysis,
    create_directory_analysis_fact,
    create_directory_concept,
)


class TestCalculateScore:
    @pytest.mark.parametrize(
        ("importance", "expected"),
        [
            (DirectoryImportance.CORE, 50.0),
            (DirectoryImportance.SUPPORTING, 30.0),
            (DirectoryImportance.UTILITY, 15.0),
        ],
    )
    def test_returns_importance_score(
        self,
        importance: DirectoryImportance,
        expected: float,
    ) -> None:
        directory = create_directory_analysis(
            path=ProjectRelativePath(Path("sample")),
            concept=create_directory_concept(
                importance=importance,
            ),
            fact=create_directory_analysis_fact(
                public_symbol_count=0,
            ),
        )

        assert (
            calculate_score(
                entry=directory,
                max_public_symbol_count=10,
            )
            == expected
        )

    def test_returns_public_symbol_score(self) -> None:
        directory = create_directory_analysis(
            path=ProjectRelativePath(Path("sample")),
            concept=create_directory_concept(
                importance=DirectoryImportance.UTILITY,
            ),
            fact=create_directory_analysis_fact(
                public_symbol_count=5,
            ),
        )

        assert (
            calculate_score(
                entry=directory,
                max_public_symbol_count=10,
            )
            == 40.0
        )

    def test_returns_zero_public_score_when_max_is_zero(self) -> None:
        directory = create_directory_analysis(
            path=ProjectRelativePath(Path("sample")),
            concept=create_directory_concept(
                importance=DirectoryImportance.CORE,
            ),
            fact=create_directory_analysis_fact(
                public_symbol_count=0,
            ),
        )

        assert (
            calculate_score(
                entry=directory,
                max_public_symbol_count=0,
            )
            == 50.0
        )


class TestRankDirectoriesByScore:
    def test_returns_empty_tuple_for_empty_directories(self) -> None:
        assert rank_directories_by_score(()) == ()

    def test_ranks_by_score(self) -> None:
        utility = create_directory_analysis(
            path=ProjectRelativePath(Path("utility")),
            concept=create_directory_concept(
                importance=DirectoryImportance.UTILITY,
            ),
            fact=create_directory_analysis_fact(
                public_symbol_count=10,
            ),
        )
        supporting = create_directory_analysis(
            path=ProjectRelativePath(Path("supporting")),
            concept=create_directory_concept(
                importance=DirectoryImportance.SUPPORTING,
            ),
            fact=create_directory_analysis_fact(
                public_symbol_count=5,
            ),
        )
        core = create_directory_analysis(
            path=ProjectRelativePath(Path("core")),
            concept=create_directory_concept(
                importance=DirectoryImportance.CORE,
            ),
            fact=create_directory_analysis_fact(
                public_symbol_count=1,
            ),
        )

        result = rank_directories_by_score((utility, supporting, core))

        assert result == (
            utility,
            core,
            supporting,
        )

    def test_uses_importance_as_tie_breaker(self) -> None:
        core = create_directory_analysis(
            path=ProjectRelativePath(Path("core")),
            concept=create_directory_concept(
                importance=DirectoryImportance.CORE,
            ),
            fact=create_directory_analysis_fact(
                public_symbol_count=0,
            ),
        )
        supporting = create_directory_analysis(
            path=ProjectRelativePath(Path("supporting")),
            concept=create_directory_concept(
                importance=DirectoryImportance.SUPPORTING,
            ),
            fact=create_directory_analysis_fact(
                public_symbol_count=4,
            ),
        )

        result = rank_directories_by_score((supporting, core))

        assert result == (
            supporting,
            core,
        )

    def test_ranks_by_importance_when_all_public_symbol_counts_are_zero(
        self,
    ) -> None:
        utility = create_directory_analysis(
            path=ProjectRelativePath(Path("utility")),
            concept=create_directory_concept(
                importance=DirectoryImportance.UTILITY,
            ),
            fact=create_directory_analysis_fact(
                public_symbol_count=0,
            ),
        )
        supporting = create_directory_analysis(
            path=ProjectRelativePath(Path("supporting")),
            concept=create_directory_concept(
                importance=DirectoryImportance.SUPPORTING,
            ),
            fact=create_directory_analysis_fact(
                public_symbol_count=0,
            ),
        )
        core = create_directory_analysis(
            path=ProjectRelativePath(Path("core")),
            concept=create_directory_concept(
                importance=DirectoryImportance.CORE,
            ),
            fact=create_directory_analysis_fact(
                public_symbol_count=0,
            ),
        )

        result = rank_directories_by_score((utility, supporting, core))

        assert result == (
            core,
            supporting,
            utility,
        )
