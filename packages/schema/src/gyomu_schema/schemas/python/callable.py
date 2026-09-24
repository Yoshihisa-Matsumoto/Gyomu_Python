from pydantic import BaseModel

from gyomu_schema.schemas.python.parameter import ParameterAnalysis
from gyomu_schema.schemas.python.type.expression import StatementAnalysis
from gyomu_schema.schemas.python.type.type_analysis import TypeAnalysis


class CallableAnalysisBase(BaseModel):
    parameters: tuple[ParameterAnalysis, ...]
    return_type: TypeAnalysis | None
    is_async: bool
    is_ellipsis_only: bool
    statements: tuple[StatementAnalysis, ...]
