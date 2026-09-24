from enum import StrEnum

from pydantic import BaseModel

from gyomu_schema.schemas.python.type.type_analysis import TypeAnalysis


class ParameterKind(StrEnum):
    """Represents the kind of a Python function parameter."""

    POSITIONAL_ONLY = "positional_only"
    """Positional-only parameter kind."""

    POSITIONAL_OR_KEYWORD = "positional_or_keyword"
    """Positional or keyword parameter kind."""

    VAR_POSITIONAL = "var_positional"
    """Variable positional parameter kind (*args)."""

    KEYWORD_ONLY = "keyword_only"
    """Keyword-only parameter kind."""

    VAR_KEYWORD = "var_keyword"
    """Variable keyword parameter kind (**kwargs)."""


class ParameterAnalysis(BaseModel):
    """Represents analysis of a Python function parameter containing its name, kind,
    type, and default value.
    """

    name: str
    """The name of the parameter."""

    kind: ParameterKind
    """The kind of the parameter."""

    type: TypeAnalysis | None
    """The type analysis of the parameter, if available."""

    default: None
    """The default value of the parameter."""
