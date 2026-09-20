import asyncio
import sys
from os import getcwd
from pathlib import Path

from dotenv import load_dotenv
from gyomu_docstring.update.process import process_docstring_update
from gyomu_infra.logger import logger
from gyomu_python_analysis.analysis.initialize import (
    initialize_project_context,
    initialize_project_from_workspace,
)
from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
from gyomu_python_analysis.analysis.workspace import (
    find_root,
    initialize_workspace_context,
)
from gyomu_python_analysis.project.workspace import WorkspaceRootKind
from gyomu_schema.option.update import (
    UpdateDebugInfoOption,
    UpdateOption,
)
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Success


async def update_with_real_llm(
    project_full_path: FullPath, source_project_relative_path: ProjectRelativePath
) -> None:
    load_dotenv()
    result = initialize_project_context(
        project_root=project_full_path,
        source_root=ProjectRelativePath(Path("src")),
    )
    if isinstance(result, Failure):
        print(repr(result.failure()))
        return

    assert isinstance(result, Success)

    project_context = result.unwrap()

    file_path = source_project_relative_path

    option = UpdateOption(
        debug_info=UpdateDebugInfoOption(
            dump_to_file=True,
            updated_symbol_docstring=True,
            file_update_plan=True,
            rendered_symbol_docstring=True,
            docstring_update_plan=True,
            docstring_update_context=True,
        ),
        # action=UpdateActionOption(no_llm_request=True),
        no_check_cache=True,
    )
    result = load_file_analysis_context(
        context=project_context, file_path=file_path, option=option
    )
    assert isinstance(result, Success)

    file_context = result.unwrap()
    result = await process_docstring_update(
        context=project_context, file_context=file_context, option=option
    )
    if isinstance(result, Failure):
        failure = result.failure()
        print(failure)
        if failure.__cause__:
            print(failure.__cause__)
    assert isinstance(result, Success)


async def main():
    args = sys.argv[1:]
    current_path = FullPath(Path(getcwd()))
    result = find_root(current_path)
    if isinstance(result, Failure):
        logger.error_object(result.failure())
        return
    workspace = result.unwrap()
    assert workspace.kind == WorkspaceRootKind.UV_WORKSPACE
    result = initialize_workspace_context(workspace)
    if isinstance(result, Failure):
        logger.error_object(result.failure())
        return
    workspace_context = result.unwrap()
    target_package = next(
        project
        for project in workspace_context.projects
        if project.config.name == args[0]
    )
    if target_package is None:
        logger.error(f"{args[0]} Not Found")
        return
    package_fullpath = FullPath(workspace_context.config.path / target_package.path)
    project_context = initialize_project_from_workspace(
        workspace_context.config, target_package
    )
    target_file_path = find_included_file(project_context.included_files, args[1])
    if target_file_path is None:
        logger.error(f"{args[1]} Not Found on {project_context.project_root}")
        return

    await update_with_real_llm(
        package_fullpath,
        target_file_path,
    )


def find_included_file(
    included_files: frozenset[ProjectRelativePath],
    path: str,
) -> ProjectRelativePath | None:
    return next(
        (
            included_file
            for included_file in included_files
            if included_file.match(path)
        ),
        None,
    )


if __name__ == "__main__":
    asyncio.run(main())
