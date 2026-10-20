from collections.abc import Mapping
from dataclasses import dataclass

from gyomu_schema.error.base import BaseError
from gyomu_schema.schemas.python.types import DeclarationIdentity, ProjectRelativePath
from gyomu_schema.schemas.types import FullPath


@dataclass(frozen=True)
class MissingTypeAnnotation:
    identity: DeclarationIdentity


@dataclass(frozen=True)
class FileMissingTypeAnnotation:
    project_relative_path: ProjectRelativePath
    missing_annotations: tuple[MissingTypeAnnotation, ...]


class ProjectMissingTypeAnnotationError(BaseError):
    def __init__(
        self,
        message: str,
        *,
        project_name: str,
        project_root: FullPath,
        error_files: tuple[FileMissingTypeAnnotation, ...],
        context: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=context,
            details=details,
        )
        self.project_name = project_name
        self.project_root = project_root
        self.error_files = error_files
