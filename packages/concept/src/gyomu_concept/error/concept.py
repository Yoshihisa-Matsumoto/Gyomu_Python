from collections.abc import Mapping
from pathlib import Path
from typing import Literal

from gyomu_schema.error.base import BaseError
from gyomu_schema.schemas.python.types import DeclarationIdentity

type ConceptPhase = Literal[
    "context-build",
    "file-summary",
    "directory-summary",
    "package-concept",
    "concept-build",
    "export",
]
"""Represents the execution phase of concept processing."""


class ConceptError(BaseError):
    """Base error class for concept processing failures, containing package, file,
    phase, and identity context.
    """

    def __init__(
        self,
        message: str,
        *,
        package_name: str,
        file_path: Path,
        phase: ConceptPhase,
        identity: DeclarationIdentity | None,
        context: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=context,
            details=details,
        )
        self.package_name = package_name
        self.file_path = file_path
        self.phase = phase
        self.identity = identity
