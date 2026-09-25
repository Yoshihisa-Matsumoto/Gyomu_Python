from gyomu_docstring.update.process import process_docstring_update
from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.option.update import UpdateOption
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.utility.context import caller_context
from returns.result import Failure, Result, Success


async def run_docstring_action(
    project_context: ProjectContext,
    source_project_relative_path: ProjectRelativePath,
    option: UpdateOption,
) -> Result[None, GyomuError]:

    file_path = source_project_relative_path
    context = caller_context()

    file_analysis_result = load_file_analysis_context(
        context=project_context, file_path=file_path, option=option
    )
    if isinstance(file_analysis_result, Failure):
        return file_analysis_result.alt(
            lambda error: GyomuError(
                "fail to analyze source file",
                domain="snapshot",
                operation="run_docstring_action",
                reason="external_failure",
                context=context,
                details={"file_path": file_path},
            ).chain(error)
        )

    file_context = file_analysis_result.unwrap()
    docstring_update_result = await process_docstring_update(
        context=project_context, file_context=file_context, option=option
    )
    if isinstance(docstring_update_result, Failure):
        return docstring_update_result.alt(
            lambda error: GyomuError(
                "fail to update docstring",
                domain="snapshot",
                operation="run_docstring_action",
                reason="external_failure",
                context=context,
                details={"file_path": file_path},
            ).chain(error)
        )
    return Success(None)
