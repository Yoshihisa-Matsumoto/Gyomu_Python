import json
from pathlib import Path

from gyomu_config.gyomu.path import resolve_gyomu_config_path
from gyomu_infra.filesystem.file_io import read_json_data
from gyomu_schema.error.config import ConfigError
from gyomu_schema.utility.serialization import validate_json
from pydantic import BaseModel
from returns.result import Failure, Result, Success


def load_gyomu_config_section[R: BaseModel](
    section_name: str, model_type: type[R], default: R
) -> Result[R, ConfigError]:
    file_path: Path = resolve_gyomu_config_path()
    if not file_path.exists():
        return Success(default)

    read_result = read_json_data(file_path)
    if isinstance(read_result, Failure):
        return read_result.alt(
            lambda error: ConfigError(
                "fail to read gyomu config", phase="load", source="json"
            ).chain(error)
        )
    json_data = read_result.unwrap()

    sections = section_name.split(".")
    if not section_name or any(not section for section in sections):
        return Failure(
            ConfigError(
                "Invalid config section path.",
                phase="path-resolve",
                source="json",
                details={"section_name": section_name},
            )
        )

    for section in sections:
        if section not in json_data:
            return Success(default)

        section_data = json_data.get(section)

        if not isinstance(section_data, dict):
            return Failure(
                ConfigError(
                    "Expected a JSON object at the section.",
                    phase="path-resolve",
                    source="json",
                    details={"section": section, "total-section-name": section_name},
                )
            )
        json_data = section_data

    return validate_json(model_type=model_type, data=json.dumps(json_data)).alt(
        lambda error: ConfigError(
            "fail to parse gyomu config", phase="validate", source="json"
        ).chain(error)
    )
