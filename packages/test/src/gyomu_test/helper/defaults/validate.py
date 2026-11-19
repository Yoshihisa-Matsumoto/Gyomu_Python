import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from gyomu_infra.filesystem.file_io import ensure_directory, write_text
from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.tools.mypy.check import check_file
from gyomu_schema.schemas.python.types import ProjectRelativePath
from returns.result import Failure, Result, Success

from gyomu_test.error.test import GyomuTestError


def _prepare(project_context: ProjectContext) -> Result[Path, GyomuTestError]:
    full_path = project_context.project_root / "test_support" / "validation_workspace"
    result = ensure_directory(full_path)
    if isinstance(result, Failure):
        return result.alt(
            lambda error: GyomuTestError(
                "fail to create validation_workspace folder"
            ).chain(error)
        )
    init_path = full_path / "__init__.py"
    if not init_path.exists():
        write_result = write_text(path=init_path, content="")
        if isinstance(write_result, Failure):
            return write_result.alt(
                lambda error: GyomuTestError("fail to create __init__.py").chain(error)
            )
    return Success(full_path)


def validate_file(
    file_path: Path,
    root_project_context: ProjectContext,
    project_context: ProjectContext,
    workspace_context: WorkspaceContext,
) -> Result[None, GyomuTestError]:
    prepare_result = _prepare(project_context)
    if isinstance(prepare_result, Failure):
        return prepare_result

    validation_workspace = prepare_result.unwrap()

    try:
        with TemporaryDirectory(dir=validation_workspace) as temp_dir:
            temp_file_path = Path(temp_dir) / file_path.name
            shutil.copy2(file_path, temp_file_path)
            init_path = Path(temp_dir) / "__init__.py"
            if not init_path.exists():
                write_result = write_text(path=init_path, content="")
                if isinstance(write_result, Failure):
                    return write_result.alt(
                        lambda error: GyomuTestError(
                            "fail to create __init__.py"
                        ).chain(error)
                    )
            check_result = check_file(
                file_path=ProjectRelativePath(
                    temp_file_path.relative_to(root_project_context.project_root)
                ),
                project_context=project_context,
                root_project_context=root_project_context,
                workspace_context=workspace_context,
            )
            if isinstance(check_result, Failure):
                return check_result.alt(
                    lambda error: GyomuTestError("mypy error").chain(error)
                )
            mypy_result = check_result.unwrap()
            if not mypy_result.success:
                return Failure(
                    GyomuTestError(
                        "Mypy Type Error",
                        details={
                            "diagnostics": mypy_result.diagnostics,
                            "details": mypy_result.details,
                        },
                    )
                )

            project_relative_path = temp_file_path.relative_to(
                root_project_context.project_root
            )

            file_result = load_file_analysis_context(
                context=root_project_context,
                file_path=ProjectRelativePath(project_relative_path),
            )
            if isinstance(file_result, Failure):
                return file_result.alt(
                    lambda error: GyomuTestError("fail to load temp file").chain(error)
                )
            return Success(None)
    except OSError as error:
        return Failure(GyomuTestError("fail to prepare validation file").chain(error))
