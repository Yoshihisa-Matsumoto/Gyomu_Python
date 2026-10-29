from typing import cast

from gyomu_schema.error.config import ConfigError
from pydantic import BaseModel
from returns.result import Failure, Result

from gyomu_config.cache.file import FileConfigCache, FileConfigCacheKey
from gyomu_config.file.internal.retrieve import (
    retrieve_single_config,
)
from gyomu_config.request import ComplexConfigRequest, _ResolvedPathRequest


class ConfigManager:
    def __init__(self) -> None:
        self._cache: FileConfigCache[BaseModel] = FileConfigCache()

    def retrieve_complex_config[T: BaseModel, C](
        self,
        request: ComplexConfigRequest[T, C],
    ) -> Result[T | None, ConfigError]:
        paths_result = request.paths_resolver.get_paths(request.context)
        if isinstance(paths_result, Failure):
            return paths_result

        configs: list[T] = []

        for path in paths_result.unwrap():
            key = FileConfigCacheKey(
                path=path,
                config_type=request.config_type,
            )

            cached_result = self._cache.get(key)
            if isinstance(cached_result, Failure):
                return cached_result

            cached_config = cached_result.unwrap()
            if cached_config is not None:
                configs.append(cast(T, cached_config))
                continue

            resolved_request = _ResolvedPathRequest[T](
                config_type=request.config_type,
                path=path,
            )
            config_result = retrieve_single_config(resolved_request)
            if isinstance(config_result, Failure):
                return config_result

            config = config_result.unwrap()
            if config is None:
                continue

            add_result = self._cache.add_with_current_state(key, config)
            if isinstance(add_result, Failure):
                return add_result

            configs.append(config)

        return request.merge_policy.merge(
            configs=tuple(configs),
            default=request.default_value,
        )
