from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath


def get_directory_concept_path(
    context: ProjectContext,
    target_directory: ProjectRelativePath,
    option: ConceptOption | None = None,
) -> FullPath:
    """Get the full path for a directory concept.

    Calculates the full file system path for a directory concept JSON file within the
    project structure.

    Args:
        context (ProjectContext): Project context providing the root directory.
        target_directory (ProjectRelativePath): Project-relative path of the target
            directory.
        option (ConceptOption | None): Optional concept configuration options.

    Returns:
        FullPath: The full path to the directory concept file.
    """
    return FullPath(
        context.project_root
        / ".gyomu"
        / (
            "cache"
            if option and option.action and option.action.write_to_temp_folder
            else "concept"
        )
        / target_directory
        / "$Directory.json"
    )
