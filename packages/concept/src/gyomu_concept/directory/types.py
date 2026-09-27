from dataclasses import dataclass

from gyomu_schema.schemas.concept.directory.concept import DirectoryConcept


@dataclass(frozen=True)
class BuildResult:
    concept: DirectoryConcept

    changed: bool
