from gyomu_schema.error.config import ConfigError
from pydantic import BaseModel
from returns.result import Failure, Result

from gyomu_config.file.internal.retrieve import (
    _ResolvedPathRequest,
    retrieve_single_config,
)
from gyomu_config.request import ComplexConfigRequest


def retrieve_complex_config[T: BaseModel, C](
    request: ComplexConfigRequest[T, C],
) -> Result[T | None, ConfigError]:
    paths_result = request.paths_resolver.get_paths(request.context)

    if isinstance(paths_result, Failure):
        return paths_result

    configs: list[T] = []

    for path in paths_result.unwrap():
        config_result = retrieve_single_config(
            request=_ResolvedPathRequest(
                config_type=request.config_type,
                path=path,
            )
        )

        if isinstance(config_result, Failure):
            return config_result

        config = config_result.unwrap()

        if config is not None:
            configs.append(config)

    return request.merge_policy.merge(
        configs=tuple(configs),
        default=request.default_value,
    )
