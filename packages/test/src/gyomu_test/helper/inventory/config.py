from dataclasses import dataclass
from pathlib import Path

from gyomu_config.request import ConfigRequest
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.error.config import ConfigError
from gyomu_schema.schemas.config.test.model_defaults import ModelDefaults
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.types import PythonPath
from returns.result import Result, Success

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
