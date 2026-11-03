from typing import cast

from gyomu_schema.error.config import ConfigError
from pydantic import BaseModel
from returns.result import Failure, Result, Success

from gyomu_config.cache.file import FileConfigCache, FileConfigCacheKey
from gyomu_config.file.internal.retrieve import (
    retrieve_single_config,
)
from gyomu_config.request import (
    BaseComplexConfigRequest,
    ComplexConfigExtractorRequest,
    ComplexConfigRequest,
    _ResolvedPathRequest,
)


class ConfigManager:
    def __init__(self) -> None:
        self._cache: FileConfigCache[BaseModel] = FileConfigCache()

    def _retrieve_configs[T: BaseModel, C](
        self,
        request: BaseComplexConfigRequest[T, C],
    ) -> Result[tuple[T, ...], ConfigError]:
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
        return Success(tuple(configs))

    def retrieve_complex_config[T: BaseModel, C](
        self,
        request: ComplexConfigRequest[T, C],
    ) -> Result[T | None, ConfigError]:
        return self._retrieve_configs(request).bind(
            lambda configs: request.merge_policy.merge(
                configs=configs,
                default=request.default_value,
            )
        )

    def retrieve_extracted_config[T: BaseModel, R: BaseModel, C](
        self,
        request: ComplexConfigExtractorRequest[T, R, C],
    ) -> Result[R | None, ConfigError]:
        configs_result = self._retrieve_configs(request)
        if isinstance(configs_result, Failure):
            return configs_result

        extracted_configs: list[R] = []

        for config in configs_result.unwrap():
            extracted_result = request.extractor.extract(
                config, context=request.context
            )
            if isinstance(extracted_result, Failure):
                return extracted_result
            extracted = extracted_result.unwrap()
            if extracted is not None:
                extracted_configs.append(extracted)

        return request.merge_policy.merge(
            configs=tuple(extracted_configs),
            default=request.default_value,
        )
