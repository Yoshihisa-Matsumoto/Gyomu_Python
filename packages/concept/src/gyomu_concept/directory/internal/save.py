from gyomu_concept.directory.internal.path import get_directory_concept_path
from gyomu_concept.error.concept import ConceptError
from gyomu_infra.filesystem.file_io import write_json
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.directory.concept import DirectoryConcept
from gyomu_schema.schemas.python.types import ProjectRelativePath
from returns.result import Result


def save_directory_concept(
    context: ProjectContext,
    target_directory: ProjectRelativePath,
    concept: DirectoryConcept,
    option: ConceptOption | None = None,
) -> Result[None, ConceptError]:
    concept_full_path = get_directory_concept_path(context, target_directory, option)
    return write_json(
        path=concept_full_path, value_type=DirectoryConcept, value=concept
    ).alt(
        lambda error: ConceptError(
            message="fail to save Directory Concept",
            file_path=target_directory,
            package_name=context.config.name,
            phase="directory-summary",
            identity=None,
        ).chain(error)
    )
