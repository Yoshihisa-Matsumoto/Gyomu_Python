from pydantic import BaseModel

from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.type.type_analysis import TypeExpression


class DecoratorArgument(BaseModel):
    """Represents an argument passed to a decorator, containing a type expression and an
    optional name.
    """

    expression: TypeExpression
    """The type expression representing the argument value."""

    name: str | None = None
    """The optional name of the argument."""


class DecoratorAnalysis(BaseModel):
    """Represents analysis information for a decorator, including its name, arguments,
    and source location.
    """

    name: str
    """The name of the decorator."""

    arguments: tuple[DecoratorArgument, ...]
    """The arguments passed to the decorator."""

    location: SourceLocation | None
    """The optional source code location of the decorator."""
