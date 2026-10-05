from gyomu_concept.error.document import DocumentBuilderError
from gyomu_python_analysis.analysis.workspace import find_root
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.types import FullPath
from gyomu_schema.utility.context import caller_context
from returns.result import Failure, Result, Success


def get_knowledge_path(
    context: ProjectContext, option: ConceptOption | None = None
) -> FullPath:
    return FullPath(
        context.project_root
        / ".gyomu"
        / (
            "cache"
            if option and option.action and option.action.write_to_temp_folder
            else "knowledge"
        )
    )


def get_root_knowledge_path(
    context: ProjectContext, option: ConceptOption | None = None
) -> Result[FullPath, DocumentBuilderError]:
    repository_root_result = find_root(context.project_root)
    if isinstance(repository_root_result, Failure):
        return repository_root_result.alt(
            lambda error: DocumentBuilderError(
                message=f"Failed to find repository root: {error}",
                phase="context-build",
                file_path=context.project_root,
                context=caller_context(),
                package_name=context.config.name,
            )
        )
    workspace_root = repository_root_result.unwrap().path
    return Success(
        workspace_root
        / ".gyomu"
        / (
            "cache"
            if option and option.action and option.action.write_to_temp_folder
            else "knowledge"
        )
    )
