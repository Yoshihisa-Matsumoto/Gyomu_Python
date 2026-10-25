from collections.abc import Mapping
from typing import Literal

from gyomu_schema.error.base import BaseError, caller_context

type ConfigPhase = Literal[
    "load", "parse", "decode", "validate", "path-resolve", "save"
]
"""Represents the configuration lifecycle phase in which an error occurred."""

type ConfigSource = Literal["env", "yaml", "json", "toml"]
"""Represents the source of configuration data or files."""


class ConfigError(BaseError):
    """Configuration error."""

    def __init__(
        self,
        message: str,
        *,
        phase: ConfigPhase,
        source: ConfigSource,
        schema: object | None = None,
        context: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        if context is None:
            context = caller_context()
        super().__init__(
            message,
            context=context,
            details=details,
        )
        self.source = source
        self.schema = schema
        self.phase = phase
