from gyomu_infra.filesystem.file_io import write_json
from gyomu_schema.error.config import ConfigError
from pydantic import BaseModel
from returns.result import Failure, Result

from gyomu_config.request import ConfigRequest


def save_config[T: BaseModel, C](
    request: ConfigRequest[T, C], value: T
) -> Result[None, ConfigError]:
    file_path_result = request.path_resolver.get_path(request.context)
    if isinstance(file_path_result, Failure):
        return file_path_result
    return write_json(
        path=file_path_result.unwrap(), value=value, value_type=request.config_type
    ).alt(
        lambda error: ConfigError(
            source="json", message="fail to save config file", phase="save"
        ).chain(error)
    )
