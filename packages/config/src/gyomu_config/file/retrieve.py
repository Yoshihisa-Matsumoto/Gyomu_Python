from gyomu_schema.error.config import ConfigError
from pydantic import BaseModel
from returns.result import Failure, Result

from gyomu_config.file.internal.retrieve import retrieve_single_config
from gyomu_config.request import ConfigRequest, _ResolvedPathRequest


def retrieve_config[T: BaseModel, C](
    request: ConfigRequest[T, C],
) -> Result[T | None, ConfigError]:
    file_path_result = request.path_resolver.get_path(request.context)
    if isinstance(file_path_result, Failure):
        return file_path_result
    file_path = file_path_result.unwrap()
    return retrieve_single_config(
        request=_ResolvedPathRequest[T](config_type=request.config_type, path=file_path)
    )
