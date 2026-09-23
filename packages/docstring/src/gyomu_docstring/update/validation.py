from gyomu_infra.process.executor import execute
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Result, Success

from gyomu_docstring.error.update import UpdateError


def run_ruff_format(
    source_path: ProjectRelativePath,
    *,
    project_root: FullPath,
    file_context: FileAnalysisContext,
) -> Result[None, UpdateError]:
    return _run_ruff(
        ("ruff", "format", str(source_path)),
        project_root=project_root,
        file_context=file_context,
        operation="format",
    )


def run_ruff_check(
    source_path: ProjectRelativePath,
    *,
    project_root: FullPath,
    file_context: FileAnalysisContext,
) -> Result[None, UpdateError]:
    return _run_ruff(
        ("ruff", "check", str(source_path)),
        project_root=project_root,
        file_context=file_context,
        operation="check",
    )


def _run_ruff(
    command: tuple[str, ...],
    *,
    project_root: FullPath,
    file_context: FileAnalysisContext,
    operation: str,
) -> Result[None, UpdateError]:
    result = execute(
        command,
        cwd=project_root,
    )
    print(command)
    print(project_root)

    return result.alt(
        lambda error: UpdateError(
            f"fail to execute ruff {operation}",
            file_path=file_context.analysis.module_name,
            phase="post-update",
            identity=None,
            context="gyomu_docstring.update._run_ruff",
        ).chain(error)
    ).bind(
        lambda process_result: (
            Success(None)
            if process_result.exit_code == 0
            else Failure(
                UpdateError(
                    f"ruff {operation} failed",
                    file_path=file_context.analysis.module_name,
                    phase="post-update",
                    identity=None,
                    context="gyomu_docstring.update._run_ruff",
                    details={
                        "exit_code": process_result.exit_code,
                        "stdout": process_result.stdout,
                        "stderr": process_result.stderr,
                    },
                )
            )
        )
    )


def validate_source(
    source_path: ProjectRelativePath,
    *,
    project_root: FullPath,
    file_context: FileAnalysisContext,
) -> Result[None, UpdateError]:
    return run_ruff_format(
        source_path, project_root=project_root, file_context=file_context
    ).bind(
        lambda _: run_ruff_check(
            source_path, project_root=project_root, file_context=file_context
        )
    )
