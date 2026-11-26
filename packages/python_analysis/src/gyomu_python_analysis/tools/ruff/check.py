import sys

from gyomu_infra.process.executor import execute
from gyomu_schema.schemas.python.types import WorkspaceRelativePath
from returns.result import Failure, Result, Success

from gyomu_python_analysis.error.tools import RuffCheckExecutionError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.tools.ruff.config import for_file, for_project, for_workspace
from gyomu_python_analysis.tools.ruff.models import RuffCheckConfig, RuffCheckResult


def _run_ruff(
    command: list[str], config: RuffCheckConfig
) -> Result[RuffCheckResult, RuffCheckExecutionError]:

    run_result = execute(command=command, cwd=config.working_directory)
    if isinstance(run_result, Failure):
        return run_result.alt(
            lambda error: RuffCheckExecutionError(
                message="fail to execute ruff", command=command
            ).chain(error)
        )

    process_result = run_result.unwrap()

    if process_result.exit_code == 0:
        return Success(
            RuffCheckResult(
                name=str(config.target),
                diagnostics=(),
            )
        )
    elif process_result.exit_code == 1:
        lines = process_result.stdout.splitlines()
        lines.extend(process_result.stderr.splitlines())
        return Success(
            RuffCheckResult(
                name=str(config.target),
                diagnostics=tuple(lines),
                details={"command": command},
            )
        )
    else:
        return Failure(
            RuffCheckExecutionError(
                message="unexpected error",
                details={
                    "stdout": process_result.stdout,
                    "stderr": process_result.stderr,
                },
                command=command,
            )
        )


def _check_format(
    config: RuffCheckConfig,
) -> Result[RuffCheckResult, RuffCheckExecutionError]:

    command = [
        sys.executable,
        "-m",
        "ruff",
        "format",
        "--check",
        str(config.target),
    ]
    return _run_ruff(command=command, config=config)


def _format(
    config: RuffCheckConfig,
) -> Result[RuffCheckResult, RuffCheckExecutionError]:
    format_command = [
        sys.executable,
        "-m",
        "ruff",
        "format",
        str(config.target),
    ]
    format_result = _run_ruff(command=format_command, config=config)
    if isinstance(format_result, Failure):
        return format_result

    import_command = [
        sys.executable,
        "-m",
        "ruff",
        "check",
        "--select",
        "I",
        "--fix",
        str(config.target),
    ]
    return _run_ruff(command=import_command, config=config)


def _check_lint(
    config: RuffCheckConfig,
) -> Result[RuffCheckResult, RuffCheckExecutionError]:

    command = [
        sys.executable,
        "-m",
        "ruff",
        "check",
        str(config.target),
    ]
    return _run_ruff(command=command, config=config)


def format_file(
    workspace_relative_file_path: WorkspaceRelativePath,
    workspace_context: WorkspaceContext,
) -> Result[RuffCheckResult, RuffCheckExecutionError]:
    config = for_file(
        workspace_relative_file_path=workspace_relative_file_path,
        workspace_context=workspace_context,
    )
    return _format(config=config)


def check_file_format(
    workspace_relative_file_path: WorkspaceRelativePath,
    workspace_context: WorkspaceContext,
) -> Result[RuffCheckResult, RuffCheckExecutionError]:
    config = for_file(
        workspace_relative_file_path=workspace_relative_file_path,
        workspace_context=workspace_context,
    )
    return _check_format(config=config)


def check_project_format(
    target_project_context: ProjectContext,
    workspace_context: WorkspaceContext,
) -> Result[RuffCheckResult, RuffCheckExecutionError]:
    config = for_project(
        target_project_context=target_project_context,
        workspace_context=workspace_context,
    )
    return _check_format(config=config)


def check_workspace_format(
    workspace_context: WorkspaceContext,
) -> Result[RuffCheckResult, RuffCheckExecutionError]:
    config = for_workspace(
        workspace_context=workspace_context,
    )
    return _check_format(config=config)


def check_file_lint(
    workspace_relative_file_path: WorkspaceRelativePath,
    workspace_context: WorkspaceContext,
) -> Result[RuffCheckResult, RuffCheckExecutionError]:
    config = for_file(
        workspace_relative_file_path=workspace_relative_file_path,
        workspace_context=workspace_context,
    )
    return _check_lint(config=config)


def check_project_lint(
    target_project_context: ProjectContext,
    workspace_context: WorkspaceContext,
) -> Result[RuffCheckResult, RuffCheckExecutionError]:
    config = for_project(
        target_project_context=target_project_context,
        workspace_context=workspace_context,
    )
    return _check_lint(config=config)


def check_workspace_lint(
    workspace_context: WorkspaceContext,
) -> Result[RuffCheckResult, RuffCheckExecutionError]:
    config = for_workspace(
        workspace_context=workspace_context,
    )
    return _check_lint(config=config)
