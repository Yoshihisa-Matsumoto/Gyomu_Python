from dataclasses import dataclass
from typing import Literal

from gyomu_schema.schemas.concept.directory.concept import DirectoryImportance
from gyomu_schema.schemas.concept.package.analysis import (
    DirectoryAnalysis,
    PackageAnalysis,
)

from gyomu_facts.package.rank import rank_directories_by_score


@dataclass(frozen=True)
class TopScoreDirectorySelection:
    limit: int | None
    strategy: Literal["top-score"] = "top-score"


@dataclass(frozen=True)
class ImportanceDirectorySelection:
    limits: dict[DirectoryImportance, int]
    strategy: Literal["importance"] = "importance"


type DirectorySelectionOption = (
    TopScoreDirectorySelection | ImportanceDirectorySelection
)


@dataclass
class PackageFacts:
    def __init__(self, analysis: PackageAnalysis):
        self.analysis = analysis

    def get_ranked_directories(
        self, option: DirectorySelectionOption
    ) -> tuple[DirectoryAnalysis, ...]:
        if isinstance(option, TopScoreDirectorySelection):
            ranked = rank_directories_by_score(self.analysis.directories)

            if option.limit is None:
                return ranked

            return ranked[: option.limit]

        return self._select_by_importance(option)

    def _select_by_importance(
        self, option: ImportanceDirectorySelection
    ) -> tuple[DirectoryAnalysis, ...]:
        selected: list[DirectoryAnalysis] = []

        for importance, limit in option.limits.items():
            directories = [
                directory
                for directory in self.analysis.directories
                if directory.concept.importance == importance
            ]
            selected.extend(directories[:limit])

        return tuple(selected)
