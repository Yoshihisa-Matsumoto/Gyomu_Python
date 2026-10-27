from collections.abc import Mapping
from typing import Literal

from gyomu_schema.error.base import BaseError, caller_context
from gyomu_schema.schemas.python.types import DeclarationIdentity, PythonPath

type UpdatePhase = Literal[
    "context-build", "update-plan", "merge-plan", "apply-merge", "update", "post-update"
]
"""Represents the phase of the docstring update process."""


class UpdateError(BaseError):
    """Docstring Update error."""

    file_path: PythonPath
    phase: UpdatePhase
    identity: DeclarationIdentity | None

    def __init__(
        self,
        message: str,
        *,
        file_path: PythonPath,
        phase: UpdatePhase,
        identity: DeclarationIdentity | None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=caller_context(),
            details=details,
        )
        self.file_path = file_path
        self.phase = phase
        self.identity = identity
