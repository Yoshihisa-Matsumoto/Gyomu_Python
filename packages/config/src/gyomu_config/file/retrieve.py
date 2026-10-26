from gyomu_infra.filesystem.file_io import read_json
from gyomu_schema.error.config import ConfigError
from pydantic import BaseModel
from returns.result import Failure, Result, Success

from gyomu_config.request import ConfigRequest


def retrieve_config[T: BaseModel, C](
    request: ConfigRequest[T, C],
) -> Result[T | None, ConfigError]:
    file_path_result = request.path_resolver.get_path(request.context)
    if isinstance(file_path_result, Failure):
        return file_path_result
    file_path = file_path_result.unwrap()
    if not file_path.exists():
        return Success(None)
    return read_json(path=file_path, model_type=request.config_type).alt(
        lambda error: ConfigError(
            source="json", message="fail to read config file", phase="load"
        ).chain(error)
    )
