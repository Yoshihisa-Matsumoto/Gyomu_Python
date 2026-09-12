from dataclasses import dataclass

from griffe import GriffeLoader
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath


@dataclass
class ProjectContext:
    def __init__(
        self, project_root: FullPath, source_root: ProjectRelativePath
    ) -> None:
        self.project_root = project_root
        self.source_root = source_root
        search_path = project_root / source_root
        self.loader = GriffeLoader(
            search_paths=[search_path],
        )
