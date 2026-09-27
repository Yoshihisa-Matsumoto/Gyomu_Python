from pydantic import BaseModel


class PydanticFieldAnalysis(BaseModel):
    """Defines the analysis results of a Pydantic field, including its default source,
    description, alias, and requirement status.
    """

    default_source: str | None
    """The source of the default value, if any."""

    description: str | None
    """The description of the field, if any."""

    alias: str | None
    """The alias name of the field, if any."""

    required: bool
    """Indicates whether the field is required."""
