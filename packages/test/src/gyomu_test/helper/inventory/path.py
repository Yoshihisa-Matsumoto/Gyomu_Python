from pathlib import Path

from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.schemas.python.types import PythonPath
from gyomu_schema.schemas.types import FullPath


def get_default_config_path(
    python_path: PythonPath, project_context: ProjectContext
) -> FullPath:

    relative_path = Path(python_path.replace(".", "/") + ".default.json")
    return FullPath(project_context.project_root / ".gyomu" / "config" / relative_path)
