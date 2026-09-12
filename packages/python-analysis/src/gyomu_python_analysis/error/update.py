from collections.abc import Mapping
from typing import Literal

from gyomu_schema.error.base import BaseError
from gyomu_schema.schemas.python.types import DeclarationIdentity, PythonPath

type UpdatePhase = Literal[
    "context-build", "update-plan", "merge-plan", "apply-merge", "update"
]


class UpdateError(BaseError):
    """Docstring Update error."""

    def __init__(
        self,
        message: str,
        *,
        file_path: PythonPath,
        phase: UpdatePhase,
        identity: DeclarationIdentity | None,
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
        self.identity = identity
