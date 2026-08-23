from typing import Literal, Mapping

from gyomu_schema.error.base import BaseError

type ConfigPhase = Literal["load", "parse", "decode", "validate"]
type ConfigSource = Literal["env", "yaml", "json", "toml"]


class ConfigError(BaseError):
    """Configuration error."""

    def __init__(
        self,
        message: str,
        *,
        source: ConfigSource,
        schema: object,
        phase: ConfigPhase,
        context: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=context,
            details=details,
        )
        self.source = source
        self.schema = schema
        self.phase = phase
