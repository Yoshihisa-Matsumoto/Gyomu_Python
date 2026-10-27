from collections.abc import Mapping
from dataclasses import dataclass

from gyomu_schema.error.base import BaseError
from gyomu_schema.schemas.python.types import DeclarationIdentity, ProjectRelativePath
from gyomu_schema.schemas.types import FullPath


@dataclass
class FunctionInformation:
    function_name: str
    file_path: ProjectRelativePath


@dataclass(frozen=True)
class DuplicateHelper:
    target_identity: DeclarationIdentity
    functions: tuple[FunctionInformation, ...]


@dataclass(frozen=True)
class MissingTypeAnnotation(Exception):
    identity: DeclarationIdentity


@dataclass(frozen=True)
class InvalidReference(Exception):
    identity: DeclarationIdentity
    reference: str


@dataclass(frozen=True)
class FileInventoryError(Exception):
    project_relative_path: ProjectRelativePath
    missing_annotations: tuple[MissingTypeAnnotation, ...]
    reference_errors: tuple[InvalidReference, ...]


class ProjectInventoryError(BaseError):
    project_name: str
    project_root: FullPath
    error_files: tuple[FileInventoryError, ...]
    duplicates: tuple[DuplicateHelper, ...]

    def __init__(
        self,
        message: str,
        *,
        project_name: str,
        project_root: FullPath,
        error_files: tuple[FileInventoryError, ...],
        duplicates: tuple[DuplicateHelper, ...],
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
        self.duplicates = duplicates
