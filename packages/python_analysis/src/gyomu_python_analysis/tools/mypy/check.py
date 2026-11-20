import os
import sys

from gyomu_infra.logger import logger
from gyomu_infra.process.executor import execute
from gyomu_schema.schemas.python.types import ProjectRelativePath
from returns.result import Failure, Result, Success

from gyomu_python_analysis.error.tools import MypyCheckExecutionError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.tools.mypy.config import for_file, for_project, for_workspace
from gyomu_python_analysis.tools.mypy.models import (
    MypyCheckConfig,
    MypyCheckReport,
    MypyCheckResult,
    MypyCheckResults,
    MypyTarget,
)


def check_project_target(
    target: MypyTarget,
    target_project_context: ProjectContext,
    workspace_root_project_context: ProjectContext,
    workspace_context: WorkspaceContext,
) -> Result[MypyCheckResult, MypyCheckExecutionError]:

    target_config = for_project(
        target=target,
        target_project_context=target_project_context,
        workspace_root_project_context=workspace_root_project_context,
        workspace_context=workspace_context,
    )
    return _execute_mypy(config=target_config)


def check_project(
    target_project_context: ProjectContext,
    workspace_root_project_context: ProjectContext,
    workspace_context: WorkspaceContext,
) -> Result[MypyCheckReport, MypyCheckExecutionError]:

    source_result = check_project_target(
        target=MypyTarget.SOURCE,
        target_project_context=target_project_context,
        workspace_root_project_context=workspace_root_project_context,
        workspace_context=workspace_context,
    )
    if isinstance(source_result, Failure):
        return source_result

    test_support_result = check_project_target(
        target=MypyTarget.TEST_SUPPORT,
        target_project_context=target_project_context,
        workspace_root_project_context=workspace_root_project_context,
        workspace_context=workspace_context,
    )
    if isinstance(test_support_result, Failure):
        return test_support_result

    tests_result = check_project_target(
        target=MypyTarget.TESTS,
        target_project_context=target_project_context,
        workspace_root_project_context=workspace_root_project_context,
        workspace_context=workspace_context,
    )
    if isinstance(tests_result, Failure):
        return tests_result

    return Success(
        MypyCheckReport(
            results=MypyCheckResults(
                src=source_result.unwrap(),
                test_support=test_support_result.unwrap(),
                tests=tests_result.unwrap(),
            )
        )
    )


def check_workspace_target(
    target: MypyTarget,
    workspace_context: WorkspaceContext,
) -> Result[MypyCheckResult, MypyCheckExecutionError]:

    target_config = for_workspace(
        target=target,
        workspace_context=workspace_context,
    )
    return _execute_mypy(config=target_config)


def check_workspace(
    workspace_context: WorkspaceContext,
) -> Result[MypyCheckReport, MypyCheckExecutionError]:

    source_result = check_workspace_target(
        target=MypyTarget.SOURCE,
        workspace_context=workspace_context,
    )
    if isinstance(source_result, Failure):
        return source_result

    test_support_result = check_workspace_target(
        target=MypyTarget.TEST_SUPPORT,
        workspace_context=workspace_context,
    )
    if isinstance(test_support_result, Failure):
        return test_support_result

    tests_result = check_workspace_target(
        target=MypyTarget.TESTS,
        workspace_context=workspace_context,
    )
    if isinstance(tests_result, Failure):
        return tests_result

    return Success(
        MypyCheckReport(
            results=MypyCheckResults(
                src=source_result.unwrap(),
                test_support=test_support_result.unwrap(),
                tests=tests_result.unwrap(),
            )
        )
    )


def check_file(
    workspace_relative_file_path: ProjectRelativePath,
    target_project_context: ProjectContext,
    workspace_root_project_context: ProjectContext,
    workspace_context: WorkspaceContext,
) -> Result[MypyCheckResult, MypyCheckExecutionError]:
    config = for_file(
        workspace_relative_file_path=workspace_relative_file_path,
        target_project_context=target_project_context,
        workspace_root_project_context=workspace_root_project_context,
        workspace_context=workspace_context,
    )
    return _execute_mypy(config=config)


def _execute_mypy(
    config: MypyCheckConfig,
) -> Result[MypyCheckResult, MypyCheckExecutionError]:
    if not config.targets:
        logger.warning("No targets configured. skip mypy")
        return Success(
            MypyCheckResult(
                name=str(config.target) if config.target is not None else "",
                diagnostics=(),
                skipped_reason="No targets configured",
            )
        )

    mypypath = (
        os.pathsep.join(map(str, config.mypy_path))
        if config.mypy_path is not None
        else None
    )
    env: dict[str, str] | None = (
        {"MYPYPATH": mypypath} if mypypath is not None else None
    )

    command = [
        sys.executable,
        "-m",
        "mypy",
        "--config-file",
        str(config.config_file),
    ]

    if config.cache_dir is not None:
        command.extend(
            [
                "--cache-dir",
                str(config.cache_dir),
            ]
        )
    else:
        command.append("--no-incremental")

    if config.explicit_package_bases:
        command.append("--explicit-package-bases")

    command.extend(str(path) for path in config.targets)

    run_result = execute(command=command, cwd=config.working_directory, env=env)
    if isinstance(run_result, Failure):
        return run_result.alt(
            lambda error: MypyCheckExecutionError(
                message="fail to execute mypy", command=command, env=env
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
        lines = process_result.stdout.splitlines()
        if lines:
            return Success(
                MypyCheckResult(
                    name=str(config.target) if config.target is not None else "",
                    diagnostics=tuple(lines),
                    details={"command": command, "env": env},
                )
            )
        return Failure(
            MypyCheckExecutionError(
                message="unexpected error",
                details={
                    "stdout": process_result.stdout,
                    "stderr": process_result.stderr,
                },
                command=command,
                env=env,
            )
        )
    else:
        return Failure(
            MypyCheckExecutionError(
                message="unexpected error",
                details={
                    "stdout": process_result.stdout,
                    "stderr": process_result.stderr,
                },
                command=command,
                env=env,
            )
        )
