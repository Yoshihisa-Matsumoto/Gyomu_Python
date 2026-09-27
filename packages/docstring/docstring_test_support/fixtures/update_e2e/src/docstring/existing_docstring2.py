from collections.abc import Mapping

CONFIG_NAME: str = "default"
"""Name of the configuration."""

CONFIG_OPTIONS: Mapping[str, str] = {}
"""Configuration options."""


type ConfigValue = (
    str | int | bool | object | list[str] | list[int] | list[bool] | list[object]
)
"""Value2 type supported by the configuration."""


type ConfigMapping = Mapping[str, ConfigValue]
"""Mapping type used for configuration values."""
