from collections.abc import Mapping

CONFIG_NAME: str = "default"
"""Name of the configuration value."""

CONFIG_OPTIONS: Mapping[str, str] = {}
"""Mapping of available configuration options."""


type ConfigValue = (
    str | int | bool | object | list[str] | list[int] | list[bool] | list[object]
)
"""Value type supported by the configuration."""


type ConfigMapping = Mapping[str, ConfigValue]
"""Mapping from configuration names to values."""
