from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EnvironmentLoaderOption:
    variables: Mapping[str, str]
    use_dot_env: bool = False
    dot_env_path: Path | None = None


@dataclass(frozen=True)
class BaseFileLoaderOption:
    file_path: Path


@dataclass(frozen=True)
class JsonLoaderOption(BaseFileLoaderOption):
    pass


@dataclass(frozen=True)
class YamlLoaderOption(BaseFileLoaderOption):
    pass


@dataclass(frozen=True)
class TomlLoaderOption(BaseFileLoaderOption):
    pass


type ConfigLoaderOption = (
    EnvironmentLoaderOption | JsonLoaderOption | YamlLoaderOption | TomlLoaderOption
)
