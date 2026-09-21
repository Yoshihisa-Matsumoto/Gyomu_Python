from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EnvironmentLoaderOption:
    """Defines configuration options for loading environment variables."""

    variables: Mapping[str, str]
    """Mapping of environment variables."""

    use_dot_env: bool = False
    """Flag indicating whether to load a .env file."""

    dot_env_path: Path | None = None
    """Path to the .env file, if any."""


@dataclass(frozen=True)
class BaseFileLoaderOption:
    """Base options for file-based configuration loaders."""

    file_path: Path
    """Path to the configuration file."""


@dataclass(frozen=True)
class JsonLoaderOption(BaseFileLoaderOption):
    """Options for loading configuration from a JSON file."""

    pass


@dataclass(frozen=True)
class YamlLoaderOption(BaseFileLoaderOption):
    """Options for loading configuration from a YAML file."""

    pass


@dataclass(frozen=True)
class TomlLoaderOption(BaseFileLoaderOption):
    """Options for loading configuration from a TOML file."""

    pass


type ConfigLoaderOption = (
    EnvironmentLoaderOption | JsonLoaderOption | YamlLoaderOption | TomlLoaderOption
)
"""Type alias representing any supported configuration loader option."""
