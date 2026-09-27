from gyomu_concept.directory.types import BuildResult
from gyomu_concept.error.concept import ConceptError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.types import FullPath
from returns.result import Result


def build_directory_concept_from_path(
    context: ProjectContext,
    target_directory: FullPath,
    option: ConceptOption | None = None,
) -> Result[BuildResult, ConceptError]: ...
