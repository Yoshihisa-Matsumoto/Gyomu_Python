from collections.abc import Mapping
from pathlib import Path
from typing import Literal

from gyomu_schema.error.base import BaseError

type DocumentBuildPhase = Literal[
    "context-build", "section-build", "document-build", "translate", "render", "export"
]


class DocumentBuilderError(BaseError):
    def __init__(
        self,
        message: str,
        *,
        package_name: str,
        phase: DocumentBuildPhase,
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
