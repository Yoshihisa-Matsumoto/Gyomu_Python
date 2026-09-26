from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from griffe import GriffeLoader
from gyomu_schema.schemas.python.types import ProjectRelativePath, WorkspaceRelativePath
from gyomu_schema.schemas.types import FullPath
from pydantic import TypeAdapter
from typing_extensions import TypeForm


@dataclass
class PyProjectConfig:
    path: WorkspaceRelativePath
    name: str
    version: str
    description: str | None
    formatter_line_length: int
    _toml_data: Mapping[str, Any]

    def get_attribute[T](
        self,
        parameter: str,
        return_type: TypeForm[T],
    ) -> T | None:
        value: Any = self._get_toml_value(parameter)

        if value is None:
            return None

        adapter = TypeAdapter(return_type)

        return adapter.validate_python(value)

    def _get_toml_value(self, parameter: str) -> Any:
        data = self._toml_data

        for key in parameter.split("."):
            if not isinstance(data, dict) or key not in data:
                return None

            data = data[key]

        return data


class ProjectContext:
    def __init__(
        self,
        project_root: FullPath,
        source_root: ProjectRelativePath,
        config: PyProjectConfig,
        included_files: frozenset[ProjectRelativePath] = frozenset(),
    ) -> None:
        self.project_root = project_root
        self.source_root = source_root
        search_path = project_root / source_root
        self.loader = GriffeLoader(
            search_paths=[search_path],
        )
        self.config = config
        self.included_files = included_files
