from dataclasses import dataclass

from gyomu_schema.schemas.concept.directory.concept import DirectoryConcept


@dataclass(frozen=True)
class BuildResult:
    """Represents the result of building a directory concept.

    Result of building a directory concept.
    """

    concept: DirectoryConcept

    changed: bool


@dataclass(frozen=True)
class BuildRootResult:
    """Represents the result of building root directory concepts.

    Result of building root directory concepts.
    """

    concepts: tuple[DirectoryConcept, ...]
    changed: bool
