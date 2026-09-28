from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath


def get_directory_concept_path(
    context: ProjectContext,
    target_directory: ProjectRelativePath,
    option: ConceptOption | None = None,
) -> FullPath:
    return FullPath(
        context.project_root
        / (
            "cache"
            if option and option.action and option.action.write_to_temp_folder
            else "concept"
        )
        / target_directory
        / "$Directory.json"
    )
