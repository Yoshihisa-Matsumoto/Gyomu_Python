from collections.abc import Mapping
from typing import Literal

from gyomu_schema.error.base import BaseError, caller_context
from gyomu_schema.schemas.python.types import PythonPath
from gyomu_schema.schemas.types import FullPath

type AnalysisPhase = Literal[
    "project-load",
    "source-file-load",
    "export-extract",
    "symbol-extract",
    "jsdoc-extract",
    "analysis",
    "post-analysis",
    "workspace-discovery",
    "snapshot",
]
"""Represents the different phases of Python code analysis."""


class AnalysisError(BaseError):
    """Python Analysis error."""

    def __init__(
        self,
        message: str,
        *,
        file_path: PythonPath | FullPath,
        phase: AnalysisPhase,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=caller_context(),
            details=details,
        )
        self.file_path = file_path
        self.phase = phase
