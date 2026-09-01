from pydantic import BaseModel

from gyomu_schema.schemas.python.parameter import ParameterAnalysis


class CallableAnalysisBase(BaseModel):
    parameters: tuple[ParameterAnalysis, ...]
    return_type: str | None
    is_async: bool
