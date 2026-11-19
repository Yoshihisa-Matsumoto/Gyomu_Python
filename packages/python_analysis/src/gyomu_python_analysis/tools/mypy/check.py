import os
import sys
from collections.abc import Mapping

from gyomu_infra.process.executor import execute
from gyomu_schema.schemas.python.types import ProjectRelativePath
from returns.result import Failure, Result, Success

from gyomu_python_analysis.error.tools import MypyCheckExecutionError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.tools.mypy.config import for_file
from gyomu_python_analysis.tools.mypy.models import (
    MypyCheckConfig,
    MypyCheckReport,
    MypyCheckResult,
    MypyTarget,
)


def check_project(
    project_context: ProjectContext,
    target: MypyTarget | None,
) -> Result[MypyCheckReport, MypyCheckExecutionError]: ...


def check_workspace(
    workspace_context: WorkspaceContext,
) -> Result[MypyCheckReport, MypyCheckExecutionError]: ...


def check_file(
    file_path: ProjectRelativePath,
    project_context: ProjectContext,
    root_project_context: ProjectContext,
    workspace_context: WorkspaceContext,
) -> Result[MypyCheckResult, MypyCheckExecutionError]:
    config = for_file(
        file_path=file_path,
        project_context=project_context,
        root_project_context=root_project_context,
        workspace_context=workspace_context,
    )
    return _execute_mypy(workspace_context=workspace_context, config=config)


def _execute_mypy(
    config: MypyCheckConfig,
    workspace_context: WorkspaceContext,
) -> Result[MypyCheckResult, MypyCheckExecutionError]:
    mypypath = (
        os.pathsep.join(map(str, config.mypy_path))
        if config.mypy_path is not None
        else None
    )
    env: Mapping[str, str] | None = (
        {"MYPYPATH": mypypath} if mypypath is not None else None
    )

    config_file_path = (
        config.config_file
        if config.config_file is not None
        else workspace_context.workspace_root.path / "pyproject.toml"
    )
    command = [
        sys.executable,
        "-m",
        "mypy",
        "--config-file",
        str(config_file_path),
    ]

    if config.cache_dir is not None:
        command.extend(
            [
                "--cache-dir",
                str(config.cache_dir),
            ]
        )

    if config.explicit_package_bases:
        command.append("--explicit-package-bases")

    command.extend(str(path) for path in config.targets)

    run_result = execute(command=command, cwd=config.working_directory, env=env)
    if isinstance(run_result, Failure):
        return run_result.alt(
            lambda error: MypyCheckExecutionError(
                message="fail to execute mypy", details={"command": command, "env": env}
            ).chain(error)
        )

    process_result = run_result.unwrap()

    if process_result.exit_code == 0:
        return Success(
            MypyCheckResult(
                name=str(config.target) if config.target is not None else "",
                diagnostics=(),
            )
        )
    elif process_result.exit_code == 1:
        return Success(
            MypyCheckResult(
                name=str(config.target) if config.target is not None else "",
                diagnostics=tuple(process_result.stdout.split("/n")),
                details={"command": command, "env": env},
            )
        )
    else:
        return Failure(
            MypyCheckExecutionError(
                message="unexpected error",
                details={
                    "stdout": process_result.stdout,
                    "stderr": process_result.stderr,
                    "command": command,
                    "env": env,
                },
            )
        )
