from gyomu_infra.filesystem.file_io import read_json
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.directory.concept import DirectoryConcept
from gyomu_schema.schemas.python.types import ProjectRelativePath
from returns.result import Result, Success

from gyomu_concept.directory.internal.path import get_directory_concept_path
from gyomu_concept.error.concept import ConceptError


def load_directory_concept(
    context: ProjectContext,
    target_directory: ProjectRelativePath,
    option: ConceptOption | None = None,
) -> Result[DirectoryConcept | None, ConceptError]:
    """Load directory concept from the project directory.

    Args:
        context (ProjectContext): Project context
        target_directory (ProjectRelativePath): Target directory relative to the project
        option (ConceptOption | None): Optional concept option

    Returns:
        Result[DirectoryConcept | None, ConceptError]: Result containing the
            DirectoryConcept or None on success, or ConceptError on failure
    """
    concept_full_path = get_directory_concept_path(context, target_directory, option)
    if not concept_full_path.exists():
        return Success(None)
    return read_json(path=concept_full_path, model_type=DirectoryConcept).alt(
        lambda error: ConceptError(
            message="fail to load Directory Concept",
            file_path=target_directory,
            package_name=context.config.name,
            phase="directory-summary",
            identity=None,
        ).chain(error)
    )
