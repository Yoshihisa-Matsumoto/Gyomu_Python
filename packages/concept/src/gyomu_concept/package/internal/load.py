from gyomu_infra.filesystem.file_io import read_json
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.package.concept import PackageConcept
from returns.result import Result, Success

from gyomu_concept.error.concept import ConceptError
from gyomu_concept.package.internal.path import get_package_concept_path


def load_package_concept(
    context: ProjectContext,
    option: ConceptOption | None = None,
) -> Result[PackageConcept | None, ConceptError]:
    """Load the package concept from the project context.

    Args:
        context (ProjectContext): The project context.
        option (ConceptOption | None): Optional concept loading options.

    Returns:
        Result[PackageConcept | None, ConceptError]: A Result containing the loaded
            PackageConcept or None if not found, or a ConceptError on failure.
    """
    concept_full_path = get_package_concept_path(context, option)
    if not concept_full_path.exists():
        return Success(None)
    return read_json(path=concept_full_path, model_type=PackageConcept).alt(
        lambda error: ConceptError(
            message="fail to load Package Concept",
            file_path=concept_full_path,
            package_name=context.config.name,
            phase="package-concept",
            identity=None,
        ).chain(error)
    )
