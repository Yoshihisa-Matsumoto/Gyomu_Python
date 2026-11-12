from dataclasses import dataclass
from pathlib import Path

from gyomu_config.file.retrieve import retrieve_mandatory_config
from gyomu_config.request import ConfigRequest
from gyomu_python_analysis.project.context import ProjectContext, WorkspaceProject
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.error.config import ConfigError
from gyomu_schema.schemas.config.test.model_defaults import ModelDefaults
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.types import ProjectRelativePath, PythonPath
from gyomu_schema.schemas.testing.helper import HelperConfig
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Result, Success

from gyomu_test.error.test import GyomuTestError
from gyomu_test.helper.inventory.path import get_default_config_path


@dataclass
class DefaultConfigPathContext:
    python_path: PythonPath
    project_context: ProjectContext


class DefaultConfigPathResolver:
    def get_path(self, context: DefaultConfigPathContext) -> Result[Path, ConfigError]:
        return Success(
            get_default_config_path(
                python_path=context.python_path, project_context=context.project_context
            )
        )


def build_config_request(
    file_analysis: FileAnalysisContext, project_context: ProjectContext
) -> ConfigRequest[ModelDefaults, DefaultConfigPathContext]:
    return ConfigRequest(
        config_type=ModelDefaults,
        context=DefaultConfigPathContext(
            python_path=file_analysis.analysis.module_name,
            project_context=project_context,
        ),
        path_resolver=DefaultConfigPathResolver(),
    )


def _load_helper_config(
    project_root: FullPath,
) -> Result[HelperConfig, GyomuTestError]:
    path = project_root / ".gyomu" / "config" / "$Package.helper.json"
    default_config_result = retrieve_mandatory_config(
        config_type=HelperConfig, path=path
    )
    return default_config_result.alt(
        lambda error: GyomuTestError(
            message="fail to retrieve project helper config"
        ).chain(error)
    )


def get_helper_file_paths_from_workspace_project(
    workspace_context: WorkspaceContext,
    workspace_project: WorkspaceProject,
) -> Result[tuple[ProjectRelativePath, ...], GyomuTestError]:
    return _get_helper_file_paths(
        project_root=workspace_context.workspace_root.path / workspace_project.path
    )


def get_helper_file_paths(
    project_context: ProjectContext,
) -> Result[tuple[ProjectRelativePath, ...], GyomuTestError]:
    return _get_helper_file_paths(project_root=project_context.project_root)


def _get_helper_file_paths(
    project_root: FullPath,
) -> Result[tuple[ProjectRelativePath, ...], GyomuTestError]:
    config_result = _load_helper_config(project_root=project_root)
    if isinstance(config_result, Failure):
        return config_result

    config = config_result.unwrap()
    helper_path = Path(config.helper_directory)

    paths = dict.fromkeys(
        (
            ProjectRelativePath(helper_path / "helpers.py"),
            *(
                ProjectRelativePath(helper_path / allocation.helper_filename)
                for allocation in config.file_allocation
            ),
        )
    )

    return Success(tuple(paths))
