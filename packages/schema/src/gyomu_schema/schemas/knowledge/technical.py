from pydantic import BaseModel, ConfigDict, Field


class Installation(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "title": "Installation",
            "description": (
                "One installation or setup step required before using this package."
            ),
        },
    )

    command: str = Field(
        description="The command required to install or set up this package.",
    )

    description: str = Field(
        description="Explain when or why this installation step is required.",
    )


class Dependency(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "title": "Dependency",
            "description": (
                "Describes one important dependency that developers should be aware of."
            ),
        },
    )

    package: str = Field(
        description="The package name or dependency identifier.",
    )

    description: str = Field(
        description=(
            "Explain why this dependency exists and how it is used within this package."
        ),
    )


class Compatibility(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "title": "Compatibility",
            "description": (
                "Describes one compatibility requirement or supported environment."
            ),
        },
    )

    name: str = Field(
        description=(
            "The technology, runtime, library, or platform this compatibility "
            "note applies to."
        ),
    )

    supported: str = Field(
        description=(
            "Describe the supported version, platform, or compatibility requirement."
        ),
    )

    description: str | None = Field(
        default=None,
        description=(
            "Additional notes about compatibility, limitations, or recommendations."
        ),
    )


class TechnicalConfiguration(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "description": "One configuration item.",
        },
    )

    key: str = Field(
        description="Configuration key, option name, or environment variable.",
    )

    description: str = Field(
        description="Explain the purpose of this configuration item.",
    )

    default_value: str | None = Field(
        default=None,
        description="Default value if one exists.",
    )


class TechnicalMigration(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "description": "One migration note.",
        },
    )

    version: str = Field(
        description="Version where the migration became necessary.",
    )

    description: str = Field(
        description="Explain the migration and required changes.",
    )


class Technical(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "title": "Technical",
            "description": (
                "Technical reference for installing, configuring, and integrating "
                "this package."
            ),
        },
    )

    installation: tuple[Installation, ...] = Field(
        description=(
            "Instructions for installing or enabling this package. Include only "
            "information that is required by developers."
        ),
    )

    configuration: tuple[TechnicalConfiguration, ...] = Field(
        description="Configuration options supported by this package.",
    )

    dependencies: tuple[Dependency, ...] = Field(
        description=(
            "Important runtime, build-time, or peer dependencies that users of "
            "this package should know about."
        ),
    )

    compatibility: tuple[Compatibility, ...] = Field(
        description=(
            "Supported runtimes, libraries, module systems, and other compatibility "
            "information."
        ),
    )

    migration: tuple[TechnicalMigration, ...] = Field(
        description="Migration guides for breaking or important changes.",
    )
