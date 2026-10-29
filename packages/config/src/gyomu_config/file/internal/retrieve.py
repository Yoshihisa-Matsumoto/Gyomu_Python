from gyomu_infra.filesystem.file_io import read_json
from gyomu_schema.error.config import ConfigError
from pydantic import BaseModel
from returns.result import Result, Success

from gyomu_config.request import _ResolvedPathRequest


def retrieve_single_config[T: BaseModel](
    request: _ResolvedPathRequest[T],
) -> Result[T | None, ConfigError]:
    if not request.path.exists():
        return Success(None)
    return read_json(path=request.path, model_type=request.config_type).alt(
        lambda error: ConfigError(
            source="json", message="fail to read config file", phase="load"
        ).chain(error)
    )
