from gyomu_concept.directory.types import BuildResult
from gyomu_concept.error.concept import ConceptError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from returns.result import Result


def build_directory_concept(
    context: ProjectContext, option: ConceptOption | None = None
) -> Result[BuildResult, ConceptError]: ...
