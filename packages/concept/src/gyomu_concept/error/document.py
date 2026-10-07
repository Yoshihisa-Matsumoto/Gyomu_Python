from collections.abc import Mapping
from pathlib import Path
from typing import Literal

from gyomu_schema.error.base import BaseError

type DocumentBuildPhase = Literal[
    "context-build", "section-build", "document-build", "translate", "render", "export"
]
"""Represents the phase in which a document build error occurred."""


class DocumentBuilderError(BaseError):
    """Exception raised during document building operations.

    Args:
        message (str): Error message.
        phase (DocumentBuildPhase): Build phase where the error occurred.
        package_name (str | None): Optional package name associated with the error.
        file_path (Path | None): Optional file path associated with the error.
        section_id (str | None): Optional section ID associated with the error.
        context (str | None): Optional context information.
        details (Mapping[str, object] | None): Optional additional details mapping.
    """

    def __init__(
        self,
        message: str,
        *,
        phase: DocumentBuildPhase,
        package_name: str | None = None,
        file_path: Path | None = None,
        section_id: str | None = None,
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
        self.section_id = section_id
