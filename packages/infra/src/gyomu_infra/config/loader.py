import json
import os
import tomllib
from collections.abc import Mapping
from pathlib import Path

import yaml
from dotenv import dotenv_values
from gyomu_schema.config.config_loader_option import (
    ConfigLoaderOption,
    EnvironmentLoaderOption,
    JsonLoaderOption,
    TomlLoaderOption,
    YamlLoaderOption,
)
from gyomu_schema.convert import convert
from gyomu_schema.error.config import ConfigError, ConfigSource
from pydantic import BaseModel
from returns.result import Failure, Result, Success


class ConfigLoader:
    """Loads and validates configuration from various sources such as environment
    variables, JSON, YAML, and TOML files.
    """

    @staticmethod
    def load[T: BaseModel](
        schema: type[T],
        option: ConfigLoaderOption,
    ) -> Result[T, ConfigError]:
        """Loads and validates configuration based on the provided option.

        Args:
            schema (type[T]):
            option (ConfigLoaderOption):

        Returns:
            Result[T, ConfigError]: A Result containing the validated configuration
                model or a ConfigError.

        Raises:
            TypeError: Raised when the configuration option type is not supported.
        """
        source: ConfigSource
        if isinstance(option, EnvironmentLoaderOption):
            result = ConfigLoader._load_environment(option)
            source = "env"
        elif isinstance(option, JsonLoaderOption):
            result = ConfigLoader._load_json(option)
            source = "json"
        elif isinstance(option, YamlLoaderOption):
            result = ConfigLoader._load_yaml(option)
            source = "yaml"
        elif isinstance(option, TomlLoaderOption):
            result = ConfigLoader._load_toml(option)
            source = "toml"
        else:
            raise TypeError(f"Unsupported option: {option}")

        return result.bind(
            lambda data: ConfigLoader._validate(
                schema,
                source,
                data,
            )
        )

    @staticmethod
    def _load_environment(
        option: EnvironmentLoaderOption,
    ) -> Result[dict[str, object], ConfigError]:
        """Loads configuration data from environment variables and optional .env files.

        Args:
            option (EnvironmentLoaderOption):

        Returns:
            Result[dict[str, object], ConfigError]: A Result containing the loaded
                environment variables dictionary or a ConfigError.
        """
        environment: dict[str, str | None] = dict(os.environ)

        if option.use_dot_env:
            dotenv_path = option.dot_env_path or Path(".env")
            dotenv = dotenv_values(dotenv_path)

            # .env の値を追加
            # 実際の環境変数を優先する
            for key, value in dotenv.items():
                if key not in environment and value is not None:
                    environment[key] = value

        data: dict[str, object] = {}

        for environment_name, field_name in option.variables.items():
            value = environment.get(environment_name)

            if value is not None:
                data[field_name] = value

        return Success(data)

    @staticmethod
    def _load_json(
        option: JsonLoaderOption,
    ) -> Result[dict[str, object], ConfigError]:
        """Loads configuration data from a JSON file.

        Args:
            option (JsonLoaderOption):

        Returns:
            Result[dict[str, object], ConfigError]: A Result containing the parsed JSON
                data dictionary or a ConfigError.
        """
        try:
            with option.file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except OSError as error:
            return Failure(
                ConfigError(
                    "Failed to load configuration file.",
                    source="json",
                    schema=dict,
                    phase="load",
                    context=str(option.file_path),
                    details={"error": str(error)},
                ).chain(error)
            )
        except UnicodeDecodeError as error:
            return Failure(
                ConfigError(
                    "Failed to decode configuration file.",
                    source="json",
                    schema=dict,
                    phase="decode",
                    context=str(option.file_path),
                    details={"error": str(error)},
                ).chain(error)
            )
        except json.JSONDecodeError as error:
            return Failure(
                ConfigError(
                    "Failed to parse JSON configuration.",
                    source="json",
                    schema=dict,
                    phase="parse",
                    context=str(option.file_path),
                    details={
                        "line": error.lineno,
                        "column": error.colno,
                        "message": error.msg,
                    },
                ).chain(error)
            )

        if not isinstance(data, dict):
            return Failure(
                ConfigError(
                    "Configuration root must be an object.",
                    source="json",
                    schema=dict,
                    phase="parse",
                    context=str(option.file_path),
                )
            )

        return Success(data)

    @staticmethod
    def _load_yaml(
        option: YamlLoaderOption,
    ) -> Result[dict[str, object], ConfigError]:
        """Loads configuration data from a YAML file.

        Args:
            option (YamlLoaderOption):

        Returns:
            Result[dict[str, object], ConfigError]: A Result containing the parsed YAML
                data dictionary or a ConfigError.
        """
        try:
            with option.file_path.open("r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
        except OSError as error:
            return Failure(
                ConfigError(
                    "Failed to load configuration file.",
                    source="yaml",
                    schema=dict,
                    phase="load",
                    context=str(option.file_path),
                    details={"error": str(error)},
                ).chain(error)
            )
        except UnicodeDecodeError as error:
            return Failure(
                ConfigError(
                    "Failed to decode configuration file.",
                    source="yaml",
                    schema=dict,
                    phase="decode",
                    context=str(option.file_path),
                    details={"error": str(error)},
                ).chain(error)
            )
        except yaml.YAMLError as error:
            return Failure(
                ConfigError(
                    "Failed to parse YAML configuration.",
                    source="yaml",
                    schema=dict,
                    phase="parse",
                    context=str(option.file_path),
                    details={"error": str(error)},
                ).chain(error)
            )

        if not isinstance(data, dict):
            return Failure(
                ConfigError(
                    "Configuration root must be an object.",
                    source="yaml",
                    schema=dict,
                    phase="parse",
                    context=str(option.file_path),
                )
            )

        return Success(data)

    @staticmethod
    def _load_toml(
        option: TomlLoaderOption,
    ) -> Result[dict[str, object], ConfigError]:
        """Loads configuration data from a TOML file.

        Args:
            option (TomlLoaderOption):

        Returns:
            Result[dict[str, object], ConfigError]: A Result containing the parsed TOML
                data dictionary or a ConfigError.
        """
        try:
            with option.file_path.open("rb") as file:
                data = tomllib.load(file)
        except OSError as error:
            return Failure(
                ConfigError(
                    "Failed to load configuration file.",
                    source="toml",
                    schema=dict,
                    phase="load",
                    context=str(option.file_path),
                    details={"error": str(error)},
                ).chain(error)
            )
        except tomllib.TOMLDecodeError as error:
            return Failure(
                ConfigError(
                    "Failed to parse TOML configuration.",
                    source="toml",
                    schema=dict,
                    phase="parse",
                    context=str(option.file_path),
                    details={"error": str(error)},
                ).chain(error)
            )

        return Success(data)

    @staticmethod
    def _validate[T: BaseModel](
        schema: type[T],
        source: ConfigSource,
        data: Mapping[str, object],
    ) -> Result[T, ConfigError]:
        """Validates configuration data against the given schema model.

        Args:
            schema (type[T]):
            source (ConfigSource):
            data (Mapping[str, object]):

        Returns:
            Result[T, ConfigError]: A Result containing the validated configuration
                model instance or a ConfigError.
        """
        return convert(schema, data).alt(
            lambda error: ConfigError(
                "Configuration validation failed.",
                source=source,
                schema=schema,
                phase="validate",
                details=error.details,
                context="ConfigLoader._validate",
            ).chain(error)
        )
