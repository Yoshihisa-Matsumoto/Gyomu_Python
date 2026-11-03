from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from gyomu_schema.error.config import ConfigError
from pydantic import BaseModel
from returns.result import Result, Success


class ConfigPathResolver[C](Protocol):
    def get_path(self, context: C) -> Result[Path, ConfigError]: ...


class ConfigRequest[T: BaseModel, C]:
    def __init__(
        self,
        config_type: type[T],
        context: C,
        path_resolver: ConfigPathResolver[C],
    ) -> None:
        self.config_type = config_type
        self.context = context
        self.path_resolver = path_resolver


class _ResolvedPathRequest[T: BaseModel]:
    def __init__(
        self,
        config_type: type[T],
        path: Path,
    ) -> None:
        self.config_type = config_type
        self.path = path


class ConfigPathsResolver[C](Protocol):
    """Resolve config paths in the order expected by the merge strategy.

    Gyomu Context:
    The returned order is preserved during config retrieval and passed
    to the merge strategy without reordering.
    """

    def get_paths(
        self,
        context: C,
    ) -> Result[tuple[Path, ...], ConfigError]: ...


class MergeStrategy[T](Protocol):
    def apply(
        self,
        configs: tuple[T, ...],
        default: T | None,
    ) -> Result[T | None, ConfigError]: ...


@dataclass(frozen=True)
class FirstAvailableStrategy[T]:
    def apply(
        self,
        configs: tuple[T, ...],
        default: T | None,
    ) -> Result[T | None, ConfigError]:
        if configs:
            return Success(configs[0])

        return Success(default)


@dataclass(frozen=True)
class MergePolicy[T]:
    strategy: MergeStrategy[T]

    def merge(
        self,
        configs: tuple[T, ...],
        default: T | None = None,
    ) -> Result[T | None, ConfigError]:
        return self.strategy.apply(configs, default)


class BaseComplexConfigRequest[T: BaseModel, C]:
    def __init__(
        self,
        config_type: type[T],
        context: C,
        paths_resolver: ConfigPathsResolver[C],
    ) -> None:
        self.config_type = config_type
        self.context = context
        self.paths_resolver = paths_resolver


class ComplexConfigRequest[T: BaseModel, C](BaseComplexConfigRequest[T, C]):
    def __init__(
        self,
        config_type: type[T],
        context: C,
        paths_resolver: ConfigPathsResolver[C],
        default_value: T | None,
        merge_policy: MergePolicy[T],
    ) -> None:
        super().__init__(
            config_type=config_type, context=context, paths_resolver=paths_resolver
        )
        self.default_value = default_value
        self.merge_policy = merge_policy


class ConfigExtractor[T: BaseModel, R: BaseModel, C](Protocol):
    def extract(self, config: T, context: C) -> Result[R | None, ConfigError]: ...


class ComplexConfigExtractorRequest[T: BaseModel, R: BaseModel, C](
    BaseComplexConfigRequest[T, C]
):
    def __init__(
        self,
        config_type: type[T],
        context: C,
        paths_resolver: ConfigPathsResolver[C],
        default_value: R | None,
        extractor: ConfigExtractor[T, R, C],
        merge_policy: MergePolicy[R],
    ) -> None:
        super().__init__(
            config_type=config_type, context=context, paths_resolver=paths_resolver
        )
        self.default_value = default_value
        self.extractor = extractor
        self.merge_policy = merge_policy
