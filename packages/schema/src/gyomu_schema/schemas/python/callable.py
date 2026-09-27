from pydantic import BaseModel

from gyomu_schema.schemas.python.parameter import ParameterAnalysis
from gyomu_schema.schemas.python.type.expression import StatementAnalysis
from gyomu_schema.schemas.python.type.type_analysis import TypeAnalysis


class CallableAnalysisBase(BaseModel):
    """Base schema for analyzing Python callable objects, including parameters, return
    type, and statements.
    """

    parameters: tuple[ParameterAnalysis, ...]
    """The parameters of the callable."""

    return_type: TypeAnalysis | None
    """The return type of the callable, if any."""

    is_async: bool
    """Whether the callable is asynchronous."""

    is_ellipsis_only: bool
    """Whether the callable contains only an ellipsis body."""

    statements: tuple[StatementAnalysis, ...]
    """The statements comprising the body of the callable."""
