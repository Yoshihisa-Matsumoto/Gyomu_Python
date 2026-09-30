from gyomu_infra.filesystem.file_io import write_json
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.package.concept import PackageConcept
from returns.result import Result

from gyomu_concept.error.concept import ConceptError
from gyomu_concept.package.internal.path import get_package_concept_path


def save_package_concept(
    context: ProjectContext,
    concept: PackageConcept,
    option: ConceptOption | None = None,
) -> Result[None, ConceptError]:
    """Saves a package concept to a JSON file.

    Args:
        context (ProjectContext): Project context containing configuration and paths.
        concept (PackageConcept): Package concept to save.
        option (ConceptOption | None): Optional concept options.

    Returns:
        Result[None, ConceptError]: A Result containing None on success or a
            ConceptError on failure.
    """
    concept_full_path = get_package_concept_path(context, option)
    return write_json(
        path=concept_full_path, value_type=PackageConcept, value=concept
    ).alt(
        lambda error: ConceptError(
            message="fail to save Package Concept",
            file_path=concept_full_path,
            package_name=context.config.name,
            phase="package-concept",
            identity=None,
        ).chain(error)
    )
