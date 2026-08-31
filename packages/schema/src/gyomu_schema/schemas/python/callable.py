from gyomu_schema.schemas.python.parameter import ParameterAnalysis
from gyomu_schema.schemas.python.type import TypeAnalysis


class CallableAnalysisBase:
    parameters: tuple[ParameterAnalysis, ...]
    return_type: TypeAnalysis | None
    is_async: bool
