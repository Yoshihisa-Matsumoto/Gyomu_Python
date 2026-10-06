from collections.abc import Mapping
from typing import Literal

from gyomu_schema.error.base import BaseError

TranslationPhase = Literal[
    "translate",
    "schema-validation",
    "reconciliation",
    "retry-context",
    "retry",
    "prompt",
]
"""Represents the distinct phases of the translation process."""


class TranslationError(BaseError):
    """Translation error."""

    def __init__(
        self,
        message: str,
        *,
        phase: TranslationPhase,
        section_id: str,
        content_type: str,  # DocumentContent type
        translation_id: int | None = None,
        validation_code: str | None = None,
        context: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=context,
            details=details,
        )
        self.phase = phase
        self.section_id = section_id
        self.content_type = content_type
        self.translation_id = translation_id
        self.validation_code = validation_code
