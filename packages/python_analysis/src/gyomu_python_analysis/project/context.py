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
    """Represents configuration settings and metadata parsed from a pyproject.toml file.

    Represents configuration settings and metadata parsed from a pyproject.toml file.
    """

    path: WorkspaceRelativePath
    """The path to the project configuration file.

    The path to the project configuration file.
    """
    name: str
    """The name of the project.

    The name of the project.
    """
    version: str
    """The version string of the project.

    The version string of the project.
    """
    description: str | None
    """Optional description of the project.

    Optional description of the project.
    """
    formatter_line_length: int
    """The line length limit configured for code formatters.

    The line length limit configured for code formatters.
    """
    _toml_data: Mapping[str, Any]
    """Raw TOML data mapping loaded from the configuration file.

    Raw TOML data mapping loaded from the configuration file.
    """

    def get_attribute[T](
        self,
        parameter: str,
        return_type: TypeForm[T],
    ) -> T | None:
        """Retrieves and validates a typed attribute value from the TOML data.

        Retrieves and validates a typed attribute value from the TOML data using a
        dot-separated parameter path.

        Args:
            parameter (str): Dot-separated parameter path in the TOML data
            return_type (TypeForm[T]): Expected return type form for validation

        Returns:
            T | None: The validated attribute value, or None if not found.
        """
        value: Any = self._get_toml_value(parameter)

        if value is None:
            return None

        adapter = TypeAdapter(return_type)

        return adapter.validate_python(value)

    def _get_toml_value(self, parameter: str) -> Any:
        """Extracts a nested value from the raw TOML data.

        Extracts a nested value from the raw TOML data mapping using a dot-separated key
        path.

        Args:
            parameter (str): Dot-separated key path into the TOML data

        Returns:
            Any: The extracted TOML value, or None if the path does not exist.
        """
        data = self._toml_data

        for key in parameter.split("."):
            if not isinstance(data, dict) or key not in data:
                return None

            data = data[key]

        return data


class ProjectContext:
    """Encapsulates project context including roots, configuration, and loader.

    Encapsulates project context, including roots, configuration, loader, and included
    files.
    """

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
