from collections.abc import Mapping
from typing import Literal

from gyomu_schema.error.base import BaseError
from gyomu_schema.schemas.python.types import PythonPath

type AnalysisPhase = Literal[
    "project-load",
    "source-file-load",
    "export-extract",
    "symbol-extract",
    "jsdoc-extract",
    "analysis",
    "post-analysis",
]


class AnalysisError(BaseError):
    """Python Analysis error."""

    def __init__(
        self,
        message: str,
        *,
        file_path: PythonPath,
        phase: AnalysisPhase,
        context: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=context,
            details=details,
        )
        self.file_path = file_path
        self.phase = phase
