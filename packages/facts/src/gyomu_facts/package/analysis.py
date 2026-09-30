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
    """Represents a top-score based directory selection option with an optional limit
    and strategy.
    """

    limit: int | None
    """Optional limit on the number of selected directories."""

    strategy: Literal["top-score"] = "top-score"
    """Selection strategy identifier, fixed to 'top-score'."""


@dataclass(frozen=True)
class ImportanceDirectorySelection:
    """Represents an importance-based directory selection option with limits per
    importance level and strategy.
    """

    limits: dict[DirectoryImportance, int]
    """Mapping of directory importance levels to selection limits."""

    strategy: Literal["importance"] = "importance"
    """Selection strategy identifier, fixed to 'importance'."""


type DirectorySelectionOption = (
    TopScoreDirectorySelection | ImportanceDirectorySelection
)
"""Type alias for directory selection options, supporting top-score or
importance-based strategies.
"""


@dataclass
class PackageFacts:
    """Provides fact analysis and directory ranking capabilities for a package
    analysis.
    """

    def __init__(self, analysis: PackageAnalysis):
        self.analysis = analysis

    def get_ranked_directories(
        self, option: DirectorySelectionOption
    ) -> tuple[DirectoryAnalysis, ...]:
        """Retrieves ranked directories based on the specified selection option.

        Args:
            option (DirectorySelectionOption): Directory selection option specifying how
                directories are ranked and filtered.

        Returns:
            tuple[DirectoryAnalysis, ...]: A tuple of ranked directory analyses.
        """
        if isinstance(option, TopScoreDirectorySelection):
            ranked = rank_directories_by_score(self.analysis.directories)

            if option.limit is None:
                return ranked

            return ranked[: option.limit]

        return self._select_by_importance(option)

    def _select_by_importance(
        self, option: ImportanceDirectorySelection
    ) -> tuple[DirectoryAnalysis, ...]:
        """Selects directories based on importance level limits.

        Args:
            option (ImportanceDirectorySelection): Importance-based directory selection
                configuration.

        Returns:
            tuple[DirectoryAnalysis, ...]: A tuple of selected directory analyses
                matching importance limits.
        """
        selected: list[DirectoryAnalysis] = []

        for importance, limit in option.limits.items():
            directories = [
                directory
                for directory in self.analysis.directories
                if directory.concept.importance == importance
            ]
            selected.extend(directories[:limit])

        return tuple(selected)
