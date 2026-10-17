from dataclasses import dataclass

from gyomu_schema.schemas.python.type.type_analysis import TypeAnalysis
from gyomu_schema.schemas.python.types import DeclarationIdentity


@dataclass(frozen=True)
class ParameterInfo:
    name: str
    parameter_type: TypeAnalysis


@dataclass(frozen=True)
class HelperInventoryItem:
    function_identity: DeclarationIdentity
    function_name: str
    return_type: DeclarationIdentity
    parameters: tuple[ParameterInfo, ...]
