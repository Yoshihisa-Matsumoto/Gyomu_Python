from typing import Literal

from gyomu_facts.package.analysis import (
    ImportanceDirectorySelection,
    PackageFacts,
    TopScoreDirectorySelection,
)
from gyomu_schema.schemas.concept.directory.concept import DirectoryImportance
from gyomu_schema.schemas.concept.package.analysis import PackageAnalysis

from packages.schema.test_support.concept_helpers import create_package_analysis


def create_top_score_directory_selection(
    limit: int | None = None,
    strategy: Literal["top-score"] = "top-score",
) -> TopScoreDirectorySelection:
    return TopScoreDirectorySelection(
        limit=limit,
        strategy=strategy,
    )


def create_importance_directory_selection(
    limits: dict[DirectoryImportance, int] = {
        DirectoryImportance.CORE: 2,
        DirectoryImportance.UTILITY: 1,
        DirectoryImportance.SUPPORTING: 1,
    },
    strategy: Literal["importance"] = "importance",
) -> ImportanceDirectorySelection:
    return ImportanceDirectorySelection(
        limits=limits,
        strategy=strategy,
    )


def create_package_facts(
    analysis: PackageAnalysis = create_package_analysis(),
) -> PackageFacts:
    return PackageFacts(
        analysis=analysis,
    )
