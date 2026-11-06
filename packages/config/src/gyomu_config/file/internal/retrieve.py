from gyomu_infra.filesystem.file_io import read_json
from gyomu_schema.error.config import ConfigError
from pydantic import BaseModel
from returns.result import Failure, Result, Success

from gyomu_config.request import _ResolvedPathRequest


def retrieve_single_config[T: BaseModel](
    request: _ResolvedPathRequest[T],
) -> Result[T | None, ConfigError]:
    if not request.path.exists():
        return Success(None)
    return _load_single_config(request)


def retrieve_mandatory_single_config[T: BaseModel](
    request: _ResolvedPathRequest[T],
) -> Result[T, ConfigError]:
    if not request.path.exists():
        return Failure(
            ConfigError("config file not exist", phase="path-resolve", source="json")
        )
    return _load_single_config(request)


def _load_single_config[T: BaseModel](
    request: _ResolvedPathRequest[T],
) -> Result[T, ConfigError]:
    return read_json(path=request.path, model_type=request.config_type).alt(
        lambda error: ConfigError(
            source="json", message="fail to read config file", phase="load"
        ).chain(error)
    )
