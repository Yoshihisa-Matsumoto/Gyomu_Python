from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.types import FullPath


def get_package_concept_path(
    context: ProjectContext,
    option: ConceptOption | None = None,
) -> FullPath:
    """Get the package concept file path within the project."""

    return FullPath(
        context.project_root
        / ".gyomu"
        / (
            "cache"
            if option and option.action and option.action.write_to_temp_folder
            else "concept"
        )
        / "$Package.json"
    )
